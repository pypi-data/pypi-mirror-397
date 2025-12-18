import os
import sqlite3
import pandas

from adam.commands.export.importer import Importer
from adam.commands.export.utils_export import GeneratorStream
from adam.utils import log2, ing
from adam.utils_k8s.pods import Pods
from adam.utils_sqlite import SQLite

class SqliteImporter(Importer):
    def prefix(self):
        return 's'

    def import_from_csv(self, pod: str, namespace: str, to_session: str, from_session: str, keyspace: str, table: str, target_table: str, columns: str, multi_tables = True, create_db = False):
        csv_file = self.csv_file(from_session, table, target_table)
        db = self.db(to_session, keyspace)

        succeeded = False
        conn = None
        try:
            os.makedirs(SQLite.local_db_dir(), exist_ok=True)
            conn = sqlite3.connect(f'{SQLite.local_db_dir()}/{db}.db')

            with ing(f'[{to_session}] Uploading to Sqlite', suppress_log=multi_tables):
                bytes = Pods.read_file(pod, 'cassandra', namespace, csv_file)
                df = pandas.read_csv(GeneratorStream(bytes))

                df.to_sql(target_table, conn, index=False, if_exists='replace')

            to, _ = self.move_to_done(pod, namespace, to_session, from_session, keyspace, target_table)

            succeeded = True

            return to, to_session
        finally:
            if succeeded:
                self.remove_csv(pod, namespace, from_session, table, target_table, multi_tables)
                SQLite.clear_cache()

                if not multi_tables:
                    query = f'select * from {target_table} limit 10'
                    log2(query)
                    SQLite.run_query(query, conn_passed=conn)

            if conn:
                conn.close()