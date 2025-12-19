from adam.commands.command import Command
from adam.commands.export.export_sessions import ExportSessions
from adam.commands.export.exporter import export
from adam.repl_state import ReplState, RequiredState

class ImportSession(Command):
    COMMAND = 'import session'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ImportSession, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ImportSession.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with export(state) as exporter:
                return exporter.import_sesion(args)

    def completion(self, state: ReplState):
        # warm up cache
        ExportSessions.export_session_names(state.sts, state.pod, state.namespace)
        ExportSessions.export_session_names(state.sts, state.pod, state.namespace, export_state='pending_import')

        return {}

    def help(self, _: ReplState):
        return f'{ImportSession.COMMAND} <export-session-name>\t import files in session to Athena or SQLite'