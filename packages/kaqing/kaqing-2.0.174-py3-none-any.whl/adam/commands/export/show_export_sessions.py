from adam.commands.command import Command
from adam.commands.export.export_sessions import ExportSessions
from adam.repl_state import ReplState, RequiredState
from adam.utils import lines_to_tabular, log
from adam.utils_k8s.statefulsets import StatefulSets

class ShowExportSessions(Command):
    COMMAND = 'show export sessions'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowExportSessions, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowExportSessions.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            pod = state.pod
            if not pod:
                pod = StatefulSets.pod_names(state.sts, state.namespace)[0]

            sessions: dict[str, str] = ExportSessions.find_export_sessions(pod, state.namespace)
            log(lines_to_tabular([f'{session}\t{export_state}' for session, export_state in sorted(sessions.items(), reverse=True)],
                                    header='EXPORT_SESSION\tSTATUS', separator='\t'))

            return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{ShowExportSessions.COMMAND}\t list export sessions'