import pandas

from adam.commands.export.export_databases import export_db
from adam.commands.export.importer import Importer
from adam.commands.export.utils_export import GeneratorStream
from adam.repl_state import ReplState
from adam.utils import log2, ing
from adam.utils_k8s.pods import Pods
from adam.utils_sqlite import SQLite, sqlite

class SqliteImporter(Importer):
    def prefix(self):
        return 's'

    def import_from_csv(self, state: ReplState, from_session: str, keyspace: str, table: str, target_table: str, columns: str, multi_tables = True, create_db = False):
        csv_file = self.csv_file(from_session, table, target_table)
        pod = state.pod
        namespace = state.namespace
        to_session = state.export_session

        succeeded = False
        try:
            with ing(f'[{to_session}] Uploading to Sqlite', suppress_log=multi_tables):
                # create a connection to single keyspace
                with sqlite(to_session, keyspace) as conn:
                    bytes = Pods.read_file(pod, 'cassandra', namespace, csv_file)
                    df = pandas.read_csv(GeneratorStream(bytes))
                    df.to_sql(target_table, conn, index=False, if_exists='replace')

            to, _ = self.move_to_done(state, from_session, keyspace, target_table)

            succeeded = True

            return to, to_session
        finally:
            if succeeded:
                self.remove_csv(state, from_session, table, target_table, multi_tables)
                SQLite.clear_cache()

                if not multi_tables:
                    with export_db(state) as dbs:
                        dbs.sql(f'select * from {keyspace}.{target_table} limit 10')