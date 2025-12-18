from adam.commands.command import Command
from adam.commands.export.exporter import Exporter
from adam.repl_state import ReplState
from adam.utils import log2
from adam.utils_athena import Athena
from adam.utils_sqlite import SQLite

class DropExportDatabase(Command):
    COMMAND = 'drop export database'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(DropExportDatabase, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return DropExportDatabase.COMMAND

    def required(self):
        return [ReplState.C, ReplState.X]

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            if not len(args):
                if state.in_repl:
                    log2('Database name is required.')
                    log2()
                else:
                    log2('* Database name is missing.')
                    Command.display_help()

                return 'command-missing'

            Exporter.drop_databases(state.sts, state.pod, state.namespace, args[0])

            SQLite.clear_cache()
            Athena.clear_cache()

            if state.export_session == args[0]:
                state.export_session = None

            return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{DropExportDatabase.COMMAND} <export-database-name>\t drop export database'