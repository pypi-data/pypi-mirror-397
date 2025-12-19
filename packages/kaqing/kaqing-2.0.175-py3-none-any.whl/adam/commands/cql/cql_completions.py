from adam.commands.cql.utils_cql import cassandra_keyspaces, cassandra_table_names
from adam.commands.export.export_sessions import ExportSessions
from adam.commands.export.export_databases import ExportDatabases
from adam.config import Config
from adam.repl_state import ReplState
from adam.sql.sql_completer import SqlCompleter, SqlVariant
from adam.utils import log_timing

def cql_completions(state: ReplState) -> dict[str, any]:
    ps = Config().get('cql.alter-tables.gc-grace-periods', '3600,86400,864000,7776000').split(',')
    # warm up caches
    with log_timing('cassandra_keyspaces'):
        cassandra_keyspaces(state)
    with log_timing('cassandra_table_names'):
        cassandra_table_names(state)
    with log_timing('ExportDatabases.database_names'):
        ExportDatabases.database_names()

    expandables = {
        'keyspaces': lambda: cassandra_keyspaces(state),
        'table-props': lambda: {
            'GC_GRACE_SECONDS': ps
        },
        'export-dbs': lambda: ExportDatabases.database_names(),
        'export-sessions': lambda: ExportSessions.export_session_names(state.sts, state.pod, state.namespace),
        'export-sessions-incomplete': lambda: ExportSessions.export_session_names(state.sts, state.pod, state.namespace, export_state='pending_import'),
    }

    return SqlCompleter(
        lambda: cassandra_table_names(state),
        expandables=expandables,
        variant=SqlVariant.CQL).completions_for_nesting()