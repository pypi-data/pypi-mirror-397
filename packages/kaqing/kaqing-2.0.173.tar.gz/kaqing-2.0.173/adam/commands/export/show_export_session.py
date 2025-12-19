from adam.commands import validate_args
from adam.commands.command import Command
from adam.commands.export.export_databases import ExportDatabases
from adam.commands.export.export_sessions import ExportSessions
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2

class ShowExportSession(Command):
    COMMAND = 'show export session'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowExportSession, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowExportSession.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with validate_args(args, state, msg='Database name'):
                ExportSessions.disply_export_session(state.sts, state.pod, state.namespace, args[0])

            return state

    def completion(self, state: ReplState):
        return super().completion(state, {session: None for session in ExportSessions.export_session_names(state.sts, state.pod, state.namespace)})

    def help(self, _: ReplState):
        return f'{ShowExportSession.COMMAND} <export-session-name>\t show export session'