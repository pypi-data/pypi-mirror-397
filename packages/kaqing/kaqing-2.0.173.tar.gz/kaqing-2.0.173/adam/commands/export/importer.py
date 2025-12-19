from abc import abstractmethod

from adam.commands.export.utils_export import csv_dir
from adam.config import Config
from adam.repl_state import ReplState
from adam.utils import ing
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.utils_k8s.pods import log_prefix

class Importer:
    @abstractmethod
    def prefix(self):
        pass

    @abstractmethod
    def import_from_csv(self, state: ReplState, from_session: str, keyspace: str, table: str, target_table: str, columns: str, multi_tables = True, create_db = False):
        pass

    def move_to_done(self, state: ReplState, from_session: str, keyspace: str, target_table: str):
        pod = state.pod
        namespace = state.namespace
        to_session = state.export_session
        log_file = f'{log_prefix()}-{from_session}_{keyspace}.{target_table}.log.pending_import'

        to = f'{log_prefix()}-{to_session}_{keyspace}.{target_table}.log.done'

        CassandraNodes.exec(pod, namespace, f'mv {log_file} {to}', show_out=Config().is_debug(), shell='bash')

        return to, to_session

    def prefix_adjusted_session(self, session: str):
        if not session.startswith(self.prefix()):
            return f'{self.prefix()}{session[1:]}'

        return session

    def remove_csv(self, state: ReplState, from_session: str, table: str, target_table: str, multi_tables = True):
        pod = state.pod
        namespace = state.namespace

        with ing(f'[{from_session}] Cleaning up temporary files', suppress_log=multi_tables):
            CassandraNodes.exec(pod, namespace, f'rm -rf {self.csv_file(from_session, table, target_table)}', show_out=Config().is_debug(), shell='bash')

    def db(self, session: str, keyspace: str):
        return f'{session}_{keyspace}'

    def csv_file(self, session: str, table: str, target_table: str):
        return f'{csv_dir()}/{session}_{target_table}/{table}.csv'

    def prefix_from_importer(importer: str = ''):
        if not importer:
            return ''

        prefix = 's'

        if importer == 'athena':
            prefix = 'e'
        elif importer == 'csv':
            prefix = 'c'

        return prefix

    def importer_from_session(session: str):
        if not session:
            return None

        importer = 'csv'

        if session.startswith('s'):
            importer = 'sqlite'
        elif session.startswith('e'):
            importer = 'athena'

        return importer
