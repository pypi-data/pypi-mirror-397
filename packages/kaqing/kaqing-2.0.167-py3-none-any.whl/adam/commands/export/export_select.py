from adam.commands.command import Command
from adam.commands.export.export_databases import ExportDatabases
from adam.repl_state import ReplState, RequiredState
from adam.sql.sql_completer import SqlCompleter, SqlVariant
from adam.utils import log2
from adam.utils_athena import Athena

class ExportSelect(Command):
    COMMAND = '.select'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportSelect, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ExportSelect.COMMAND

    def required(self):
        return RequiredState.EXPORT_DB

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            if not state.export_session:
                if state.in_repl:
                    if state.device == ReplState.C:
                        log2("Select an export database first with 'use' command.")
                    else:
                        log2('cd to an export database first.')
                else:
                    log2('* export database is missing.')

                    Command.display_help()

                return 'command-missing'

            if not args:
                if state.in_repl:
                    log2('Use a SQL statement.')
                else:
                    log2('* SQL statement is missing.')

                    Command.display_help()

                return 'command-missing'

            query = ' '.join(args)

            ExportDatabases.run_query(f'select {query}', database=state.export_session)

            return state

    def completion(self, state: ReplState):
        if not state.export_session:
            return {}

        db = state.export_session

        # warm up the caches first time when x: drive is accessed
        ExportDatabases.table_names(db)
        Athena.column_names(database=db, function='export')
        Athena.column_names(partition_cols_only=True, database=db, function='export')

        return {ExportSelect.COMMAND: SqlCompleter(
            lambda: ExportDatabases.table_names(db),
            dml='select',
            expandables={
                'columns':lambda table: Athena.column_names(database=db, function='export'),
            },
            variant=SqlVariant.ATHENA
        )}

    def help(self, _: ReplState):
        return f'.<sql-select-statements>\t run queries on export database'