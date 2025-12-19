from adam.commands.command import Command
from adam.commands.export.export_databases import ExportDatabases
from adam.repl_state import ReplState
from adam.utils import log2

class ExportUse(Command):
    COMMAND = 'use'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportUse, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ExportUse.COMMAND

    def required(self):
        return [ReplState.C, ReplState.X]

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            if not args:
                state.export_session = None

                log2('Export database is unset.')

                return state

            state.export_session = args[0]

            ExportDatabases.display_export_db(state.export_session)

            return state

    def completion(self, state: ReplState):
        return super().completion(state, {n: None for n in ExportDatabases.database_names()})

    def help(self, _: ReplState):
        return f'{ExportUse.COMMAND} <export-database-name>\t use export database'