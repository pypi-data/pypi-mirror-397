import sys
from typing import TypeVar

from adam.config import Config
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.pod_exec_result import PodExecResult
from adam.utils import log, log2
from adam.utils_k8s.pods import Pods
from adam.utils_k8s.statefulsets import StatefulSets

T = TypeVar('T')

# utility collection on cassandra clusters; methods are all static
class CassandraClusters:
    def exec(sts: str, namespace: str, command: str, action: str = 'action',
             max_workers=0, show_out=True, on_any = False, shell = '/bin/sh', background = False, log_file = None) -> list[PodExecResult]:

        pods = StatefulSets.pod_names(sts, namespace)
        samples = 1 if on_any else sys.maxsize
        msg = 'd`Running|Ran ' + action + ' command onto {size} pods'
        with Pods.parallelize(pods, max_workers, samples, msg, action=action) as exec:
            results: list[PodExecResult] = exec.map(lambda pod: CassandraNodes.exec(pod, namespace, command, False, False, shell, background, log_file))
            for result in results:
                if show_out and not Config().is_debug():
                    log(result.command)
                    if result.stdout:
                        log(result.stdout)
                    if result.stderr:
                        log2(result.stderr, file=sys.stderr)

            return results

    def pod_names_by_host_id(sts: str, ns: str):
        pods = StatefulSets.pods(sts, ns)

        return {CassandraNodes.get_host_id(pod.metadata.name, ns): pod.metadata.name for pod in pods}
