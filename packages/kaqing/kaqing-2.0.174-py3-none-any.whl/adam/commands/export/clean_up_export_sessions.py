from adam.commands import validate_args
from adam.commands.command import Command
from adam.commands.export.export_sessions import ExportSessions
from adam.commands.export.exporter import Exporter
from adam.repl_state import ReplState, RequiredState
from adam.utils import log, log2

class CleanUpExportSessions(Command):
    COMMAND = 'clean up export sessions'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(CleanUpExportSessions, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return CleanUpExportSessions.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with validate_args(args, state, name='export session') as arg_str:
                sessions = [arg.strip(' ') for arg in arg_str.split(',')]
                csv_cnt, log_cnt = ExportSessions.clean_up_sessions(state.sts, state.pod, state.namespace, sessions)
                log(f'Removed {csv_cnt} csv and {log_cnt} log files.')

                ExportSessions.clear_export_session_cache()

                return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{CleanUpExportSessions.COMMAND} <export-session-name>\t clean up export session'