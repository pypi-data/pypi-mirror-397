import functools

from adam.commands.postgres.postgres_context import PostgresContext
from adam.repl_state import ReplState
from adam.utils import log2, wait_log
from adam.utils_k8s.pods import Pods

TestPG = [False]

@functools.lru_cache()
def pg_database_names(ns: str, pg_path: str):
    if TestPG[0]:
        return ['azops88_c3ai_c3']

    wait_log('Inspecting Postgres Databases...')

    pg = PostgresContext.apply(ns, pg_path)
    return [db['name'] for db in pg.databases() if db['owner'] == PostgresContext.default_owner()]

@functools.lru_cache()
def pg_table_names(ns: str, pg_path: str):
    if TestPG[0]:
        return ['C3_2_XYZ1']

    wait_log('Inspecting Postgres Database...')
    return [table['name'] for table in pg_tables(ns, pg_path) if table['schema'] == PostgresContext.default_schema()]

def pg_tables(ns: str, pg_path: str):
    pg = PostgresContext.apply(ns, pg_path)
    if pg.db:
        return pg.tables()

    return []

class PostgresPodService:
    def __init__(self, handler: 'PostgresExecHandler'):
        self.handler = handler

    def exec(self, command: str, show_out=True):
        state = self.handler.state

        pod, container = PostgresContext.pod_and_container(state.namespace)
        if not pod:
            log2('Cannot locate postgres agent or ops pod.')
            return state

        return Pods.exec(pod, container, state.namespace, command, show_out=show_out)

    def sql(self, args: list[str], background=False):
        state = self.handler.state

        query = args
        if isinstance(args, list):
            query = ' '.join(args)

        PostgresContext.apply(state.namespace, state.pg_path).run_sql(query, background=background)

class PostgresExecHandler:
    def __init__(self, state: ReplState, background=False):
        self.state = state
        self.background = background

    def __enter__(self):
        return PostgresPodService(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

def postgres(state: ReplState, background=False):
    return PostgresExecHandler(state, background=background)