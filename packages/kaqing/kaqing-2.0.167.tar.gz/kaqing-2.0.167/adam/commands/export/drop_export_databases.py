from adam.commands.command import Command
from adam.commands.export.exporter import Exporter
from adam.repl_state import ReplState
from adam.utils_athena import Athena
from adam.utils_sqlite import SQLite

class DropExportDatabases(Command):
    COMMAND = 'drop all export databases'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(DropExportDatabases, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return DropExportDatabases.COMMAND

    def required(self):
        return [ReplState.C, ReplState.X]

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            Exporter.drop_databases(state.sts, state.pod, state.namespace)

            SQLite.clear_cache()
            Athena.clear_cache()

            state.export_session = None

            return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{DropExportDatabases.COMMAND}\t drop all export databases'