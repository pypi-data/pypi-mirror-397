from adam.commands.command import Command
from adam.commands.export.export_sessions import ExportSessions
from adam.repl_state import ReplState, RequiredState

class CleanUpAllExportSessions(Command):
    COMMAND = 'clean up all export sessions'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(CleanUpAllExportSessions, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return CleanUpAllExportSessions.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            if ExportSessions.clean_up_all_sessions(state.sts, state.pod, state.namespace):
                ExportSessions.clear_export_session_cache()

            return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{CleanUpAllExportSessions.COMMAND}\t clean up all export sessions'