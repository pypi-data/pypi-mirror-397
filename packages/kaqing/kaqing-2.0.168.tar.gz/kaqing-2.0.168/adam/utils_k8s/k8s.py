from collections.abc import Callable
import re
from typing import Union

import portforward

from adam.commands.command import InvalidState
from adam.pod_exec_result import PodExecResult
from adam.repl_state import ReplState
from adam.utils import log2
from adam.utils_k8s.cassandra_clusters import CassandraClusters
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.utils_k8s.kube_context import KubeContext

def cassandra(state: ReplState, pod: str=None):
    return CassandraExecHandler(state, pod=pod)

class CassandraExecHandler:
    def __init__(self, state: ReplState, pod: str = None):
        self.state = state
        self.pod = pod
        if not pod and state.pod:
            self.pod = state.pod

    def __enter__(self):
        return self.exec

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def exec(self, command: str, action='bash', show_out = True, on_any = False, throw_err = False, shell = '/bin/sh', background = False, log_file = None) -> Union[PodExecResult, list[PodExecResult]]:
        state = self.state

        if self.pod:
            return CassandraNodes.exec(self.pod, state.namespace, command,
                                    show_out=show_out, throw_err=throw_err, shell=shell, background=background, log_file=log_file)
        elif state.sts:
            return CassandraClusters.exec(state.sts, state.namespace, command, action=action,
                                        show_out=show_out, on_any=on_any, shell=shell, background=background, log_file=log_file)

        return []

def nodetool(state: ReplState, pod: str=None, show_out=True):
    return NodetoolHandler(state, pod=pod, show_out=show_out)

class NodetoolHandler:
    def __init__(self, state: ReplState, pod:str=None, show_out=True):
        self.state = state
        self.pod = pod
        if not pod and state.pod:
            self.pod = state.pod
        self.show_out = show_out

    def __enter__(self):
        return self.exec

    def exec(self, args: str) -> Union[PodExecResult, list[PodExecResult]]:
        state = self.state

        user, pw = state.user_pass()
        command = f"nodetool -u {user} -pw {pw} {args}"

        if self.pod:
            return CassandraNodes.exec(self.pod, state.namespace, command, show_out=self.show_out)
        else:
            return CassandraClusters.exec(state.sts, state.namespace, command, action='nodetool', show_out=self.show_out)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

class PortForwardHandler:
    connections: dict[str, int] = {}

    def __init__(self, state: ReplState, local_port: int, svc_or_pod: Callable[[bool],str], target_port: int):
        self.state = state
        self.local_port = local_port
        self.svc_or_pod = svc_or_pod
        self.target_port = target_port
        self.forward_connection = None
        self.pod = None

    def __enter__(self) -> tuple[str, str]:
        state = self.state

        if not self.svc_or_pod:
            log2('No service or pod found.')

            raise InvalidState(state)

        if KubeContext.in_cluster():
            svc_name = self.svc_or_pod(True)
            if not svc_name:
                log2('No service found.')

                raise InvalidState(state)

            # cs-a526330d23-cs-a526330d23-default-sts-0 ->
            # curl http://cs-a526330d23-cs-a526330d23-reaper-service.stgawsscpsr.svc.cluster.local:8080
            groups = re.match(r'^(.*?-.*?-.*?-.*?-).*', state.sts)
            if groups:
                svc = f'{groups[1]}{svc_name}.{state.namespace}.svc.cluster.local:{self.target_port}'
                return (svc, svc)
            else:
                raise InvalidState(state)
        else:
            pod = self.svc_or_pod(False)
            if not pod:
                log2('No pod found.')

                raise InvalidState(state)

            self.pod = pod
            self.forward_connection = portforward.forward(state.namespace, pod, self.local_port, self.target_port)
            if self.inc_connection_cnt() == 1:
                self.forward_connection.__enter__()

            return (f'localhost:{self.local_port}', f'{pod}:{self.target_port}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.forward_connection:
            if not self.dec_connection_cnt():
                return self.forward_connection.__exit__(exc_type, exc_val, exc_tb)

        return False

    def inc_connection_cnt(self):
        id = self.connection_id(self.pod)
        if id not in PortForwardHandler.connections:
            PortForwardHandler.connections[id] = 1
        else:
            PortForwardHandler.connections[id] += 1

        return PortForwardHandler.connections[id]

    def dec_connection_cnt(self):
        id = self.connection_id(self.pod)
        if id not in PortForwardHandler.connections:
            PortForwardHandler.connections[id] = 0
        elif PortForwardHandler.connections[id] > 0:
            PortForwardHandler.connections[id] -= 1

        return PortForwardHandler.connections[id]

    def connection_id(self, pod: str):
        return f'{self.local_port}:{pod}:{self.target_port}'

def port_forwarding(state: ReplState, local_port: int, svc_or_pod: Callable[[bool],str], target_port: int):
    return PortForwardHandler(state, local_port, svc_or_pod, target_port)