from adam.commands import extract_options
from adam.commands.command import Command
from adam.commands.cql.utils_cql import cassandra_keyspaces, cassandra_table_names
from adam.commands.export.export_databases import ExportDatabases
from adam.commands.export.exporter import export
from adam.repl_state import ReplState, RequiredState
from adam.sql.sql_completer import SqlCompleter, SqlVariant
from adam.utils import log
from adam.utils_k8s.statefulsets import StatefulSets

class ExportTables(Command):
    COMMAND = 'export'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportTables, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ExportTables.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with extract_options(args, '--export-only') as (args, export_only):
                with export(state) as exporter:
                    return exporter.export(args, export_only=export_only)

    def completion(self, state: ReplState):
        def sc():
            return SqlCompleter(lambda: cassandra_table_names(state), expandables={
                'dml':'export',
                'columns': lambda table: ['id', '*'],
                'keyspaces': lambda: cassandra_keyspaces(state),
                'export-dbs': lambda: ExportDatabases.database_names(),
            }, variant=SqlVariant.CQL)

        if super().completion(state):
            return {f'@{p}': {ExportTables.COMMAND: sc()} for p in StatefulSets.pod_names(state.sts, state.namespace)}

        return {}

    def help(self, _: ReplState):
        return f'{ExportTables.COMMAND} [* [in KEYSPACE]] | [TABLE] [as target-name] [with consistency <level>]\t export tables to Sqlite, Athena or CSV file'