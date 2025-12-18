from typing import Union

from adam.pod_exec_result import PodExecResult
from adam.repl_state import ReplState
from adam.utils_k8s.cassandra_clusters import CassandraClusters
from adam.utils_k8s.cassandra_nodes import CassandraNodes

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