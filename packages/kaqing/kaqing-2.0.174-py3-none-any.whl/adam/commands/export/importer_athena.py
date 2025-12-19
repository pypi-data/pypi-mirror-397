import boto3

from adam.commands.export.export_databases import export_db
from adam.commands.export.importer import Importer
from adam.commands.export.utils_export import GeneratorStream
from adam.config import Config
from adam.repl_state import ReplState
from adam.utils import debug, log2, ing
from adam.utils_athena import Athena
from adam.utils_k8s.pods import Pods

class AthenaImporter(Importer):
    def ping():
        session = boto3.session.Session()
        credentials = session.get_credentials()

        return credentials is not None

    def prefix(self):
        return 'e'

    def import_from_csv(self, state: ReplState, from_session: str, keyspace: str, table: str, target_table: str, columns: str, multi_tables = True, create_db = False):
        csv_file = self.csv_file(from_session, table, target_table)
        pod = state.pod
        namespace = state.namespace
        to_session = state.export_session
        database = self.db(to_session, keyspace)

        succeeded = False
        try:
            bucket = Config().get('export.bucket', 'c3.ops--qing')

            with ing(f'[{to_session}] Uploading to S3', suppress_log=multi_tables):
                bytes = Pods.read_file(pod, 'cassandra', namespace, csv_file)

                s3 = boto3.client('s3')
                s3.upload_fileobj(GeneratorStream(bytes), bucket, f'export/{database}/{keyspace}/{target_table}/{table}.csv')

            msg: str = None
            if create_db:
                msg = f"[{to_session}] Creating database {database}"
            else:
                msg = f"[{to_session}] Creating table {target_table}"
            with ing(msg, suppress_log=multi_tables):
                query = f'CREATE DATABASE IF NOT EXISTS {database};'
                debug(query)
                Athena.query(query, 'default')

                query = f'DROP TABLE IF EXISTS {target_table};'
                debug(query)
                Athena.query(query, database)

                athena_columns = ', '.join([f'{c} string' for c in columns.split(',')])
                query = f'CREATE EXTERNAL TABLE IF NOT EXISTS {target_table}(\n' + \
                        f'    {athena_columns})\n' + \
                            "ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'\n" + \
                            'WITH SERDEPROPERTIES (\n' + \
                            '    "separatorChar" = ",",\n' + \
                            '    "quoteChar"     = "\\"")\n' + \
                        f"LOCATION 's3://{bucket}/export/{database}/{keyspace}/{target_table}'\n" + \
                            'TBLPROPERTIES ("skip.header.line.count"="1");'
                debug(query)
                try:
                    Athena.query(query, database)
                except Exception as e:
                    log2(f'*** Failed query:\n{query}')
                    raise e

            to, _ = self.move_to_done(state, from_session, keyspace, target_table)

            succeeded = True

            return to, to_session
        finally:
            if succeeded:
                self.remove_csv(state, from_session, table, target_table, multi_tables)
                Athena.clear_cache()

                if not multi_tables:
                    with export_db(state) as dbms:
                        dbms.sql(f'select * from {database}.{target_table} limit 10')