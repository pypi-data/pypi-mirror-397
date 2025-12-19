from collections.abc import Callable
from datetime import datetime
import sys
import time
from typing import TypeVar
from kubernetes import client
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL, WSClient

from adam.config import Config
from adam.utils_k8s.volumes import ConfigMapMount
from adam.pod_exec_result import PodExecResult
from adam.utils import ParallelMapHandler, log2, debug, log_exc
from .kube_context import KubeContext

from websocket._core import WebSocket

T = TypeVar('T')
_TEST_POD_EXEC_OUTS: PodExecResult = None

# utility collection on pods; methods are all static
class Pods:
    _TEST_POD_CLOSE_SOCKET: bool = False

    def set_test_pod_exec_outs(outs: PodExecResult):
        global _TEST_POD_EXEC_OUTS
        _TEST_POD_EXEC_OUTS = outs

        return _TEST_POD_EXEC_OUTS

    def delete(pod_name: str, namespace: str, grace_period_seconds: int = None):
        with log_exc(lambda e: "Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e):
            v1 = client.CoreV1Api()
            v1.delete_namespaced_pod(pod_name, namespace, grace_period_seconds=grace_period_seconds)

    def delete_with_selector(namespace: str, label_selector: str, grace_period_seconds: int = None):
        v1 = client.CoreV1Api()

        ret = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
        for i in ret.items:
            v1.delete_namespaced_pod(name=i.metadata.name, namespace=namespace, grace_period_seconds=grace_period_seconds)

    def parallelize(collection: list, max_workers: int = 0, samples = sys.maxsize, msg: str = None, action: str = 'action'):
        if not max_workers:
            max_workers = Config().action_workers(action, 0)
        if samples == sys.maxsize:
            samples = Config().action_node_samples(action, sys.maxsize)

        return ParallelMapHandler(collection, max_workers, samples = samples, msg = msg)

    def exec(pod_name: str, container: str, namespace: str, command: str,
             show_out = True, throw_err = False, shell = '/bin/sh',
             background = False,
             log_file = None,
             interaction: Callable[[any, list[str]], any] = None,
             env_prefix: str = None):
        if _TEST_POD_EXEC_OUTS:
            return _TEST_POD_EXEC_OUTS

        show_out = KubeContext.show_out(show_out)

        api = client.CoreV1Api()

        tty = True
        exec_command = [shell, '-c', command]
        if env_prefix:
            exec_command = [shell, '-c', f'{env_prefix} {command}']

        if background or command.endswith(' &'):
            # should be false for starting a background process
            tty = False

            if Config().get('repl.background-process.auto-nohup', True):
                command = command.strip(' &')
                cmd_name = ''
                if command.startswith('nodetool '):
                    cmd_name = f".{'_'.join(command.split(' ')[5:])}"

                if not log_file:
                    log_file = f'{log_prefix()}-{datetime.now().strftime("%d%H%M%S")}{cmd_name}.log'
                command = f"nohup {command} > {log_file} 2>&1 &"
                if env_prefix:
                    command = f'{env_prefix} {command}'
                exec_command = [shell, '-c', command]

        k_command = f'kubectl exec {pod_name} -c {container} -n {namespace} -- {shell} -c "{command}"'
        debug(k_command)

        resp: WSClient = stream(
            api.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            command=exec_command,
            container=container,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=tty,
            _preload_content=False,
        )

        s: WebSocket = resp.sock
        stdout = []
        stderr = []
        error_output = None
        try:
            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    frag = resp.read_stdout()
                    stdout.append(frag)
                    if show_out: print(frag, end="")

                    if interaction:
                        interaction(resp, stdout)
                if resp.peek_stderr():
                    frag = resp.read_stderr()
                    stderr.append(frag)
                    if show_out: print(frag, end="")

            with log_exc():
                # get the exit code from server
                error_output = resp.read_channel(ERROR_CHANNEL)
        except Exception as e:
            if throw_err:
                raise e
            else:
                log2(e)
        finally:
            resp.close()
            if s and s.sock and Pods._TEST_POD_CLOSE_SOCKET:
                with log_exc():
                    s.sock.close()

        return PodExecResult("".join(stdout), "".join(stderr), k_command, error_output, pod=pod_name, log_file=log_file)

    def read_file(pod_name: str, container: str, namespace: str, file_path: str):
        v1 = client.CoreV1Api()

        resp = stream(
            v1.connect_get_namespaced_pod_exec,
            name=pod_name,
            namespace=namespace,
            container=container,
            command=["cat", file_path],
            stderr=True, stdin=False,
            stdout=True, tty=False,
            _preload_content=False, # Important for streaming
        )

        s: WebSocket = resp.sock
        try:
            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    yield resp.read_stdout()

            with log_exc():
                # get the exit code from server
                error_output = resp.read_channel(ERROR_CHANNEL)
        except Exception as e:
            raise e
        finally:
            resp.close()
            if s and s.sock and Pods._TEST_POD_CLOSE_SOCKET:
                with log_exc():
                    s.sock.close()

    def get_container(namespace: str, pod_name: str, container_name: str):
        pod = Pods.get(namespace, pod_name)
        if not pod:
            return None

        for container in pod.spec.containers:
            if container_name == container.name:
                return container

        return None

    def get(namespace: str, pod_name: str):
        v1 = client.CoreV1Api()
        return v1.read_namespaced_pod(name=pod_name, namespace=namespace)

    def get_with_selector(namespace: str, label_selector: str):
        v1 = client.CoreV1Api()

        ret = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
        for i in ret.items:
            return v1.read_namespaced_pod(name=i.metadata.name, namespace=namespace)

    def create_pod_spec(name: str, image: str, image_pull_secret: str,
                        envs: list, container_security_context: client.V1SecurityContext,
                        volume_name: str, pvc_name:str, mount_path:str,
                        command: list[str]=None, sa_name : str = None, config_map_mount: ConfigMapMount = None,
                        restart_policy="Never"):
        volume_mounts = []
        if volume_name and pvc_name and mount_path:
            volume_mounts=[client.V1VolumeMount(mount_path=mount_path, name=volume_name)]

        if config_map_mount:
            volume_mounts.append(client.V1VolumeMount(mount_path=config_map_mount.mount_path, sub_path=config_map_mount.sub_path, name=config_map_mount.name()))

        container = client.V1Container(name=name, image=image, env=envs, security_context=container_security_context, command=command,
                                    volume_mounts=volume_mounts)

        volumes = []
        if volume_name and pvc_name and mount_path:
            volumes=[client.V1Volume(name=volume_name, persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name))]

        security_context = None
        if not sa_name:
            security_context=client.V1PodSecurityContext(run_as_user=1001, run_as_group=1001, fs_group=1001)

        if config_map_mount:
            volumes.append(client.V1Volume(name=config_map_mount.name(), config_map=client.V1ConfigMapVolumeSource(name=config_map_mount.config_map_name)))

        return client.V1PodSpec(
            restart_policy=restart_policy,
            containers=[container],
            image_pull_secrets=[client.V1LocalObjectReference(name=image_pull_secret)],
            security_context=security_context,
            service_account_name=sa_name,
            volumes=volumes
        )

    def create(namespace: str, pod_name: str, image: str,
               command: list[str] = None,
               secret: str = None,
               env: dict[str, any] = {},
               container_security_context: client.V1SecurityContext = None,
               labels: dict[str, str] = {},
               volume_name: str = None,
               pvc_name: str = None,
               mount_path: str = None,
               sa_name: str = None,
               config_map_mount: ConfigMapMount = None):
        v1 = client.CoreV1Api()
        envs = []
        for k, v in env.items():
            envs.append(client.V1EnvVar(name=str(k), value=str(v)))
        pod = Pods.create_pod_spec(pod_name, image, secret, envs, container_security_context, volume_name, pvc_name, mount_path, command=command,
                                   sa_name=sa_name, config_map_mount=config_map_mount)
        return v1.create_namespaced_pod(
            namespace=namespace,
            body=client.V1Pod(spec=pod, metadata=client.V1ObjectMeta(
                name=pod_name,
                labels=labels
            ))
        )

    def wait_for_running(namespace: str, pod_name: str, msg: str = None, label_selector: str = None):
        cnt = 2
        while (cnt < 302 and Pods.get_with_selector(namespace, label_selector) if label_selector else Pods.get(namespace, pod_name)).status.phase != 'Running':
            if not msg:
                msg = f'Waiting for the {pod_name} pod to start up.'

            max_len = len(msg) + 3
            mod = cnt % 3
            padded = ''
            if mod == 0:
                padded = f'\r{msg}'.ljust(max_len)
            elif mod == 1:
                padded = f'\r{msg}.'.ljust(max_len)
            else:
                padded = f'\r{msg}..'.ljust(max_len)
            log2(padded, nl=False)
            cnt += 1
            time.sleep(1)

        log2(f'\r{msg}..'.ljust(max_len), nl=False)
        if cnt < 302:
            log2(' OK')
        else:
            log2(' Timed Out')

    def completed(namespace: str, pod_name: str):
        return Pods.get(namespace, pod_name).status.phase in ['Succeeded', 'Failed']

def log_prefix():
    return Config().get('log-prefix', '/tmp/qing')