from adam.commands.command import Command
from adam.commands.export.export_databases import ExportDatabases
from adam.repl_state import ReplState, RequiredState
from adam.sql.sql_completer import SqlCompleter, SqlVariant
from adam.utils_athena import Athena

# No action body, only for a help entry and auto-completion
class ExportSelectX(Command):
    COMMAND = 'select_on_x'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportSelectX, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ExportSelectX.COMMAND

    def required(self):
        return RequiredState.EXPORT_DB

    def completion(self, state: ReplState):
        completions = {}

        if state.device == ReplState.X:
            completions = {'drop': SqlCompleter(
                lambda: ExportDatabases.table_names(state.export_session),
                dml='drop',
                expandables={
                    'export-dbs': lambda: ExportDatabases.database_names(),
                    'columns':lambda _: Athena.column_names(database=state.export_session, function='export'),
                },
                variant=SqlVariant.ATHENA
            )}

            if state.export_session:
                completions |= {dml: SqlCompleter(
                    lambda: ExportDatabases.table_names(state.export_session),
                    dml=dml,
                    expandables={
                        'export-dbs': lambda: ExportDatabases.database_names(),
                        'columns':lambda _: Athena.column_names(database=state.export_session, function='export'),
                    },
                    variant=SqlVariant.ATHENA
                ) for dml in ['select', 'preview']}

        return completions

    def help(self, _: ReplState):
        return f'<sql-select-statements>\t run queries on export database'