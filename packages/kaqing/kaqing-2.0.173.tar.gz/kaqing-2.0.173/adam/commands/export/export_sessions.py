import functools
import re

from adam.commands.export.importer import Importer
from adam.commands.export.utils_export import ExportTableStatus, csv_dir, find_files
from adam.config import Config
from adam.utils import lines_to_tabular, log, parallelize
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.utils_k8s.pods import log_prefix
from adam.utils_k8s.statefulsets import StatefulSets

class ExportSessions:
    def clear_export_session_cache():
        ExportSessions.find_export_sessions.cache_clear()
        ExportSessions.export_session_names.cache_clear()

    @functools.lru_cache()
    def export_session_names(sts: str, pod: str, namespace: str, importer: str = None, export_state = None):
        if not sts or not namespace:
            return []

        if not pod:
            pod = StatefulSets.pod_names(sts, namespace)[0]

        if not pod:
            return []

        return [session for session, state in ExportSessions.find_export_sessions(pod, namespace, importer).items() if not export_state or state == export_state]

    @functools.lru_cache()
    def find_export_sessions(pod: str, namespace: str, importer: str = None, limit = 100):
        sessions: dict[str, str] = {}

        prefix = Importer.prefix_from_importer(importer)

        log_files: list[str] = find_files(pod, namespace, f'{log_prefix()}-{prefix}*_*.log*')

        if not log_files:
            return {}

        for log_file in log_files[:limit]:
            m = re.match(f'{log_prefix()}-(.*?)_.*\.log?(.*)', log_file)
            if m:
                s = m.group(1)
                state = m.group(2) # '', '.pending_import', '.done'
                if state:
                    state = state.strip('.')
                else:
                    state = 'in_export'

                if s not in sessions:
                    sessions[s] = state
                elif sessions[s] == 'done' and state != 'done':
                    sessions[s] = state

        return sessions

    def clean_up_all_sessions(sts: str, pod: str, namespace: str):
        if not sts or not namespace:
            return False

        if not pod:
            pod = StatefulSets.pod_names(sts, namespace)[0]

        CassandraNodes.exec(pod, namespace, f'rm -rf {csv_dir()}/*', show_out=Config().is_debug(), shell='bash')
        CassandraNodes.exec(pod, namespace, f'rm -rf {log_prefix()}-*.log*', show_out=Config().is_debug(), shell='bash')

        return True

    def clean_up_sessions(sts: str, pod: str, namespace: str, sessions: list[str], max_workers = 0):
        if not sessions:
            return []

        if not max_workers:
            max_workers = Config().action_workers('export', 8)

        with parallelize(sessions, max_workers, msg='Cleaning|Cleaned up {size} export sessions') as exec:
            cnt_tuples = exec.map(lambda session: ExportSessions.clean_up_session(sts, pod, namespace, session, True))
            csv_cnt = 0
            log_cnt = 0
            for (csv, log) in cnt_tuples:
                csv_cnt += csv
                log_cnt += log

            return csv_cnt, log_cnt

    def clean_up_session(sts: str, pod: str, namespace: str, session: str, multi_tables = True):
        if not sts or not namespace:
            return 0, 0

        if not pod:
            pod = StatefulSets.pod_names(sts, namespace)[0]

        if not pod:
            return 0, 0

        csv_cnt = 0
        log_cnt = 0

        log_files: list[str] = find_files(pod, namespace, f'{log_prefix()}-{session}_*.log*')

        for log_file in log_files:
            m = re.match(f'{log_prefix()}-{session}_(.*?)\.(.*?)\.log.*', log_file)
            if m:
                table = m.group(2)

                CassandraNodes.exec(pod, namespace, f'rm -rf {csv_dir()}/{session}_{table}', show_out=not multi_tables, shell='bash')
                csv_cnt += 1

                CassandraNodes.exec(pod, namespace, f'rm -rf {log_file}', show_out=not multi_tables, shell='bash')
                log_cnt += 1

        return csv_cnt, log_cnt

    def disply_export_session(sts: str, pod: str, namespace: str, session: str):
        if not pod:
            pod = StatefulSets.pod_names(sts, namespace)[0]

        if not pod:
            return

        tables, _ = ExportTableStatus.from_session(sts, pod, namespace, session)
        log()
        log(lines_to_tabular([f'{table.keyspace}\t{table.table}\t{table.target_table}\t{"export_completed_pending_import" if table.status == "pending_import" else table.status}' for table in tables], header='KEYSPACE\tTABLE\tTARGET_TABLE\tSTATUS', separator='\t'))