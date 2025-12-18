import os
import boto3

from adam.commands.export.utils_export import ExportTableStatus
from adam.config import Config
from adam.utils import lines_to_tabular, log, log2, ing
from adam.utils_athena import Athena
from adam.utils_k8s.statefulsets import StatefulSets
from adam.utils_sqlite import SQLite

LIKE = 'e%_%'

class ExportDatabases:
    def run_query(query: str, database: str, show_query=False) -> int:
        cnt: int = 0

        if show_query:
            log2(query)

        if database.startswith('s'):
            cnt += SQLite.run_query(query, database=database)
        else:
            cnt += Athena.run_query(query, database=database)

        return cnt

    def sessions_from_dbs(dbs: list[str]):

        sessions = set()

        for db in dbs:
            sessions.add(db.split('_')[0])

        return list(sessions)

    def drop_export_dbs(db: str = None):
        dbs: list[str] = []

        if not db or db.startswith('s'):
            dbs.extend(ExportDatabases.drop_sqlite_dbs(db))
        if not db or db.startswith('e'):
            dbs.extend(ExportDatabases.drop_athena_dbs(db))

        return dbs

    def drop_sqlite_dbs(db: str = None):
        dbs = SQLite.database_names(db)
        if dbs:
            with ing(f'Droping {len(dbs)} SQLite databases'):
                try:
                    for db in dbs:
                        file_path = f'{SQLite.local_db_dir()}/{db}'
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            pass
                except:
                    pass

        return dbs

    def drop_athena_dbs(db: str = None):
        dbs = Athena.database_names(f'{db}_%' if db else LIKE)
        if dbs:
            with ing(f'Droping {len(dbs)} Athena databases'):
                for db in dbs:
                    query = f'DROP DATABASE {db} CASCADE'
                    if Config().is_debug():
                        log2(query)
                    Athena.query(query)

        with ing(f'Deleting s3 folder: export'):
            try:
                if not db:
                    db = ''

                s3 = boto3.resource('s3')
                bucket = s3.Bucket(Config().get('export.bucket', 'c3.ops--qing'))
                bucket.objects.filter(Prefix=f'export/{db}').delete()
            except:
                pass

        return dbs

    def display_export_db(export_session: str):
        if not export_session:
            return

        Athena.clear_cache()

        keyspaces = {}
        for table in ExportDatabases.table_names(export_session):
            keyspace = table.split('.')[0]
            if keyspace in keyspaces:
                keyspaces[keyspace] += 1
            else:
                keyspaces[keyspace] = 1

        log(lines_to_tabular([f'{k},{v}' for k, v in keyspaces.items()], header='SCHEMA,# of TABLES', separator=','))

    def disply_export_session(sts: str, pod: str, namespace: str, session: str):
        if not pod:
            pod = StatefulSets.pod_names(sts, namespace)[0]

        if not pod:
            return

        tables, _ = ExportTableStatus.from_session(sts, pod, namespace, session)
        log()
        log(lines_to_tabular([f'{table.keyspace}\t{table.table}\t{table.target_table}\t{"export_completed_pending_import" if table.status == "pending_import" else table.status}' for table in tables], header='KEYSPACE\tTABLE\tTARGET_TABLE\tSTATUS', separator='\t'))

    def database_names():
        return ExportDatabases.copy_database_names() + ExportDatabases.export_database_names()

    def copy_database_names():
        return list({n.split('_')[0] for n in SQLite.database_names()})

    def export_database_names():
        return list({n.split('_')[0] for n in Athena.database_names(LIKE)})

    def database_names_with_keyspace_cnt(importer: str = None):
        r = {}

        names = []
        if not importer:
            names = SQLite.database_names() + Athena.database_names(LIKE)
        elif importer == 'athena':
            names = Athena.database_names(LIKE)
        else:
            names = SQLite.database_names()

        for n in names:
            tokens = n.split('_')
            name = tokens[0]
            keyspace = None
            if len(tokens) > 1:
                keyspace = tokens[1].replace('.db', '')

            if keyspace == 'root':
                continue

            if name in r:
                r[name] += 1
            else:
                r[name] = 1

        return r

    def table_names(session: str):
        tables = []

        for session in ExportDatabases._session_database_names(session):
            if session.startswith('s'):
                for table in SQLite.table_names(database=session):
                    tables.append(f'{SQLite.keyspace(session)}.{table}')
            else:
                for table in Athena.table_names(database=session, function='export'):
                    tables.append(f'{session}.{table}')

        return tables

    def _session_database_names(db: str):
        eprefix = db
        if '_' in db:
            eprefix = db.split('_')[0]

        if db.startswith('s'):
            return SQLite.database_names(prefix=f'{eprefix}_')
        else:
            return Athena.database_names(like=f'{eprefix}_%')