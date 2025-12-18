from adam.commands.command import Command
from adam.commands.export.export_databases import ExportDatabases
from adam.config import Config
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2

class ShowColumnCounts(Command):
    COMMAND = 'show column counts on'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowColumnCounts, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowColumnCounts.COMMAND

    def required(self):
        return RequiredState.EXPORT_DB

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            if not args:
                if state.in_repl:
                    log2('Use a SQL statement.')
                else:
                    log2('* SQL statement is missing.')

                    Command.display_help()

                return 'command-missing'

            table = args[0]
            query = Config().get(f'export.column_counts_query', 'select id, count(id) as columns from {table} group by id')
            query = query.replace('{table}', table)
            ExportDatabases.run_query(query, state.export_session)

            return state

    def completion(self, state: ReplState):
        if not state.export_session:
            return {}

        return super().completion(state, lambda: {t: None for t in ExportDatabases.table_names(state.export_session)})

    def help(self, _: ReplState):
        return f'{ShowColumnCounts.COMMAND} <export-table-name>\t show column count per id'