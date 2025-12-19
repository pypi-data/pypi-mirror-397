from datetime import datetime
import time

from adam.commands import validate_args
from adam.commands.command import Command
from adam.commands.cql.utils_cql import cassandra_table_names, run_cql, table_spec
from adam.commands.export.export_databases import ExportDatabases
from adam.commands.export.export_sessions import ExportSessions
from adam.commands.export.importer import Importer
from adam.commands.export.importer_athena import AthenaImporter
from adam.commands.export.importer_sqlite import SqliteImporter
from adam.commands.export.utils_export import ExportSpec, ExportTableStatus, ExportTableSpec, ImportSpec, csv_dir, find_files, state_with_pod
from adam.config import Config
from adam.pod_exec_result import PodExecResult
from adam.repl_state import ReplState
from adam.utils import debug, log, parallelize, log2, ing, log_exc
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.utils_k8s.pods import log_prefix

class Exporter:
    def export_tables(args: list[str], state: ReplState, export_only: bool = False, max_workers = 0) -> tuple[list[str], ExportSpec]:
        if export_only:
            log2('export-only for testing')

        spec: ExportSpec = None
        with log_exc(True):
            spec = Exporter.export_spec(' '.join(args), state)

            statuses, spec = Exporter._export_tables(spec, state, max_workers=max_workers, export_state='init')
            if not statuses:
                return statuses, spec

            return Exporter._export_tables(spec, state, export_only, max_workers, 'pending_export')

        return [], None

    def export_spec(spec_str: str, state: ReplState):
        spec: ExportSpec = ExportSpec.parse_specs(spec_str)

        session = state.export_session
        if session:
            if spec.importer:
                importer_from_session = Importer.importer_from_session(session)
                if spec.importer != importer_from_session:
                    if spec.importer == 'csv':
                        prefix = Importer.prefix_from_importer(spec.importer)
                        session = f'{prefix}{session[1:]}'
                    else:
                        raise Exception(f"You're currently using {importer_from_session} export database. You cannot export tables with {spec.importer} type database.")
            else:
                spec.importer = Importer.importer_from_session(session)

            if spec.importer == 'athena' and not AthenaImporter.ping():
                raise Exception('Credentials for Athena is not present.')
        else:
            if not spec.importer:
                spec.importer = Config().get('export.default-importer', 'sqlite')

            prefix = Importer.prefix_from_importer(spec.importer)
            session = f'{prefix}{datetime.now().strftime("%Y%m%d%H%M%S")[3:]}'

            if spec.importer == 'athena' and not AthenaImporter.ping():
                raise Exception('Credentials for Athena is not present.')

            if spec.importer != 'csv':
                state.export_session = session

        spec.session = session

        return spec

    def import_session(args: list[str], state: ReplState, max_workers = 0) -> tuple[list[str], ExportSpec]:
        import_spec: ImportSpec = None
        with log_exc(True):
            import_spec = Exporter.import_spec(' '.join(args), state)
            tables, status_in_whole = ExportTableStatus.from_session(state.sts, state.pod, state.namespace, import_spec.session)
            if status_in_whole == 'done':
                log2(f'The session has been completely done - no more csv files are found.')
                return [], ExportSpec(None, None, importer=import_spec.importer, tables=[])

            spec = ExportSpec(None, None, importer=import_spec.importer, tables=[ExportTableSpec.from_status(table) for table in tables], session=import_spec.session)

            return Exporter._export_tables(spec, state, max_workers=max_workers, export_state = 'import')

        return [], None

    def import_spec(spec_str: str, state: ReplState):
        spec: ImportSpec = ImportSpec.parse_specs(spec_str)

        session = state.export_session
        if session:
            if spec.importer:
                importer = Importer.importer_from_session(state.export_session)
                if spec.importer != importer:
                    raise Exception(f"You're currently using {importer} export database. You cannot import to {spec.importer} type database.")
            else:
                spec.importer = Importer.importer_from_session(state.export_session)
                if not spec.importer:
                    spec.importer = Config().get('export.default-importer', 'sqlite')

            if spec.importer == 'athena' and not AthenaImporter.ping():
                raise Exception('Credentials for Athena is not present.')
        else:
            if not spec.importer:
                spec.importer = Importer.importer_from_session(spec.session)

            if spec.importer == 'csv':
                spec.importer = Config().get('export.default-importer', 'sqlite')

            if spec.importer == 'athena' and not AthenaImporter.ping():
                raise Exception('Credentials for Athena is not present.')

            prefix = Importer.prefix_from_importer(spec.importer)
            session = f'{prefix}{spec.session[1:]}'
            state.export_session = session

        return spec

    def _export_tables(spec: ExportSpec, state: ReplState, export_only = False, max_workers = 0, export_state = None) -> tuple[list[str], ExportSpec]:
        if not spec.keyspace:
            spec.keyspace = f'{state.namespace}_db'

        if not spec.tables:
            spec.tables = [ExportTableSpec.parse(t) for t in cassandra_table_names(state, keyspace=spec.keyspace)]

        if not max_workers:
            max_workers = Config().action_workers(f'export.{spec.importer}', 8)

        if export_state == 'init':
            CassandraNodes.exec(state.pod, state.namespace, f'rm -rf {csv_dir()}/{spec.session}_*', show_out=Config().is_debug(), shell='bash')

        action = f'[{spec.session}] Exporting|Exported'
        if export_state == 'init':
            action = f'[{spec.session}] Preparing|Prepared'
        elif export_state == 'import':
            action = f'[{spec.session}] Importing|Imported'

        with parallelize(spec.tables, max_workers, msg=action + ' {size} Cassandra tables') as exec:
            return exec.map(lambda table: Exporter.export_table(table, state, spec.session, spec.importer, export_only, len(spec.tables) > 1, consistency=spec.consistency, export_state=export_state)), spec

    def export_table(spec: ExportTableSpec, state: ReplState, session: str, importer: str, export_only = False, multi_tables = True, consistency: str = None, export_state=None):
        s: str = None

        table, target_table, columns = Exporter.resove_table_n_columns(spec, state, include_ks_in_target=False, importer=importer)

        log_file = f'{log_prefix()}-{session}_{spec.keyspace}.{target_table}.log'
        create_db = not state.export_session

        if export_state == 'init':
            Exporter.create_table_log(spec, state, session, table, target_table)
            return 'table_log_created'
        else:
            if export_state == 'pending_export':
                Exporter.export_to_csv(spec, state, session, table, target_table, columns, multi_tables=multi_tables, consistency=consistency)

            log_files: list[str] = find_files(state.pod, state.namespace, f'{log_file}*')
            if not log_files:
                return s

            log_file = log_files[0]

            status: ExportTableStatus = ExportTableStatus.from_log_file(state.pod, state.namespace, session, log_file)
            while status.status != 'done':
                if status.status == 'export_in_pregress':
                    debug('Exporting to CSV is still in progess, sleeping for 1 sec...')
                    time.sleep(1)
                elif status.status == 'exported':
                    log_file = Exporter.rename_to_pending_import(spec, state, session, target_table)
                    if importer == 'csv' or export_only:
                        return 'pending_import'
                elif status.status == 'pending_import':
                    log_file, session = Exporter.import_from_csv(spec, state, session, importer, table, target_table, columns, multi_tables=multi_tables, create_db=create_db)

                status = ExportTableStatus.from_log_file(state.pod, state.namespace, session, log_file)

            return status.status

    def create_table_log(spec: ExportTableSpec, state: ReplState, session: str, table: str, target_table: str):
        log_file = f'{log_prefix()}-{session}_{spec.keyspace}.{target_table}.log'

        CassandraNodes.exec(state.pod, state.namespace, f'rm -f {log_file}* && touch {log_file}', show_out=Config().is_debug(), shell='bash')

        return table

    def export_to_csv(spec: ExportTableSpec, state: ReplState, session: str, table: str, target_table: str, columns: str, multi_tables = True, consistency: str = None):
        db = f'{session}_{target_table}'

        CassandraNodes.exec(state.pod, state.namespace, f'mkdir -p {csv_dir()}/{db}', show_out=Config().is_debug(), shell='bash')
        csv_file = f'{csv_dir()}/{db}/{table}.csv'
        log_file = f'{log_prefix()}-{session}_{spec.keyspace}.{target_table}.log'

        suppress_ing_log = Config().is_debug() or multi_tables
        queries = []
        if consistency:
            queries.append(f'CONSISTENCY {consistency}')
        queries.append(f"COPY {spec.keyspace}.{table}({columns}) TO '{csv_file}' WITH HEADER = TRUE")
        r: PodExecResult = ing(
            f'[{session}] Dumping table {spec.keyspace}.{table}{f" with consistency {consistency}" if consistency else ""}',
            lambda: run_cql(state, ';'.join(queries), show_out=Config().is_debug(), background=True, log_file=log_file),
            suppress_log=suppress_ing_log)

        return log_file

    def rename_to_pending_import(spec: ExportTableSpec, state: ReplState, session: str, target_table: str):
        log_file = f'{log_prefix()}-{session}_{spec.keyspace}.{target_table}.log'
        to = f'{log_file}.pending_import'

        CassandraNodes.exec(state.pod, state.namespace, f'mv {log_file} {to}', show_out=Config().is_debug(), shell='bash')

        return to

    def import_from_csv(spec: ExportTableSpec, state: ReplState, session: str, importer: str, table: str, target_table: str, columns: str, multi_tables = True, create_db = False):
        im = AthenaImporter() if importer == 'athena' else SqliteImporter()
        return im.import_from_csv(state, session if session else state.export_session, spec.keyspace, table, target_table, columns, multi_tables, create_db)

    def resove_table_n_columns(spec: ExportTableSpec, state: ReplState, include_ks_in_target = False, importer = 'sqlite'):
        table = spec.table
        columns = spec.columns
        if not columns:
            columns = Config().get(f'export.{importer}.columns', f'<keys>')

        keyspaced_table = f'{spec.keyspace}.{spec.table}'
        if columns == '<keys>':
            columns = ','.join(table_spec(state, keyspaced_table, on_any=True).keys())
        elif columns == '<row-key>':
            columns = table_spec(state, keyspaced_table, on_any=True).row_key()
        elif columns == '*':
            columns = ','.join([c.name for c in table_spec(state, keyspaced_table, on_any=True).columns])

        if not columns:
            log2(f'ERROR: Empty columns on {table}.')
            return table, None, None

        target_table = spec.target_table if spec.target_table else table
        if not include_ks_in_target and '.' in target_table:
            target_table = target_table.split('.')[-1]

        return table, target_table, columns

class ExportService:
    def __init__(self, handler: 'ExporterHandler'):
        self.handler = handler

    def export(self, args: list[str], export_only=False):
        state = self.handler.state
        export_session = state.export_session
        spec: ExportSpec = None
        try:
            with state_with_pod(state) as state:
                # --export-only for testing only
                statuses, spec = Exporter.export_tables(args, state, export_only=export_only)
                if not statuses:
                    return state

                ExportSessions.clear_export_session_cache()

                if spec.importer == 'csv' or export_only:
                    ExportSessions.disply_export_session(state.sts, state.pod, state.namespace, spec.session)
                else:
                    log()
                    ExportDatabases.display_export_db(state.export_session)
        finally:
            # if exporting to csv, do not bind the new session id to repl state
            if spec and spec.importer == 'csv':
                state.export_session = export_session

        return state

    def import_sesion(self, args: list[str]):
        state = self.handler.state

        with validate_args(args, state, name='export session') as args_str:
            with state_with_pod(state) as state:
                tables, _ = Exporter.import_session(args_str, state)
                if tables:
                    ExportSessions.clear_export_session_cache()

                    log()
                    ExportDatabases.display_export_db(state.export_session)

            return state

class ExporterHandler:
    def __init__(self, state: ReplState):
        self.state = state

    def __enter__(self):
        return ExportService(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

def export(state: ReplState):
    return ExporterHandler(state)