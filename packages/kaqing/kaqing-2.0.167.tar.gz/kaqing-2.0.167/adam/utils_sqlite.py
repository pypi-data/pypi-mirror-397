import functools
import glob
import os
import sqlite3
import pandas

from adam.config import Config
from adam.utils import lines_to_tabular, log, wait_log

class CursorHandler:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def __enter__(self):
        self.cursor = self.conn.cursor()

        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()

        return False

# no state utility class
class SQLite:
    def cursor(conn: sqlite3.Connection):
        return CursorHandler(conn)

    def local_db_dir():
        return Config().get('export.sqlite.local-db-dir', '/tmp/qing-db')

    def keyspace(database: str):
        return '_'.join(database.replace(".db", "").split('_')[1:])

    def connect(session: str):
        os.makedirs(SQLite.local_db_dir(), exist_ok=True)

        conn = None

        try:
            conn = sqlite3.connect(f'{SQLite.local_db_dir()}/{session}_root.db')
            with SQLite.cursor(conn) as cursor:
                for d in SQLite.database_names(session):
                    if d != f'{session}_root.db':
                        q = f"ATTACH DATABASE '{SQLite.local_db_dir()}/{d}' AS {SQLite.keyspace(d)};"
                        cursor.execute(q)
        finally:
            pass

        return conn

    @functools.lru_cache()
    def database_names(prefix: str = None):
        wait_log('Inspecting export databases...')

        pattern = f'{SQLite.local_db_dir()}/s*.db'
        if prefix:
            pattern = f'{SQLite.local_db_dir()}/{prefix}*'
        return [os.path.basename(f) for f in glob.glob(pattern)]

    def clear_cache(cache: str = None):
        SQLite.database_names.cache_clear()
        SQLite.table_names.cache_clear()

    @functools.lru_cache()
    def table_names(database: str):
      tokens = database.replace('.db', '').split('_')
      ts_prefix = tokens[0]
      keyspace = '_'.join(tokens[1:])

      conn = None
      tables = []
      try:
         conn = sqlite3.connect(f'{SQLite.local_db_dir()}/{ts_prefix}_{keyspace}.db')
         with SQLite.cursor(conn) as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

            tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]

         return tables
      except sqlite3.Error as e:
         print(f"Error connecting to or querying the database: {e}")
         return []
      finally:
         if conn:
               conn.close()

    @functools.lru_cache()
    def column_names(tables: list[str] = [], database: str = None, function: str = 'audit', partition_cols_only = False):
        pass

    def run_query(query: str, database: str = None, conn_passed = None):
        conn = None
        try:
            if not conn_passed:
                conn = SQLite.connect(database)

            df = SQLite.query(conn_passed if conn_passed else conn, query)
            lines = ['\t'.join(map(str, line)) for line in df.values.tolist()]
            log(lines_to_tabular(lines, header='\t'.join(df.columns.tolist()), separator='\t'))

            return len(lines)
        finally:
            if conn:
                conn.close()

    def query(conn, sql: str) -> tuple[str, str, list]:
        return pandas.read_sql_query(sql, conn)
