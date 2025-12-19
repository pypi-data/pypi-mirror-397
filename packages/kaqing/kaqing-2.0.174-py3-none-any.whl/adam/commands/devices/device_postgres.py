from adam.commands.bash.bash_completer import BashCompleter
from adam.commands.command import Command, InvalidStateException
from adam.commands.devices.device import Device
from adam.commands.postgres.postgres_context import PostgresContext
from adam.commands.postgres.utils_postgres import pg_database_names, pg_table_names, postgres
from adam.repl_state import ReplState
from adam.utils import lines_to_tabular, log, log2, wait_log
from adam.utils_k8s.pods import Pods

class DevicePostgres(Command, Device):
    COMMAND = f'{ReplState.P}:'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(DevicePostgres, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return DevicePostgres.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        state.device = ReplState.P

        return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{DevicePostgres.COMMAND}\t move to Postgres Operations device'

    def ls(self, cmd: str, state: ReplState):
        if state.pg_path:
            pg: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path)
            if pg.db:
                self.show_pg_tables(pg)
            else:
                self.show_pg_databases(pg)
        else:
            self.show_pg_hosts(state)

    def cat(self, cmd: str, state: ReplState):
        if state.pod:
            return self.bash(state, state, cmd.split(' '))

        raise InvalidStateException()

    def show_pg_hosts(self, state: ReplState):
        if state.namespace:
            def line(pg: PostgresContext):
                return f'{pg.path()},{pg.endpoint()}:{pg.port()},{pg.username()},{pg.password()}'

            lines = [line(PostgresContext.apply(state.namespace, pg)) for pg in PostgresContext.hosts(state.namespace)]

            log(lines_to_tabular(lines, 'NAME,ENDPOINT,USERNAME,PASSWORD', separator=','))
        else:
            def line(pg: PostgresContext):
                return f'{pg.path()},{pg.namespace},{pg.endpoint()}:{pg.port()},{pg.username()},{pg.password()}'

            lines = [line(PostgresContext.apply(state.namespace, pg)) for pg in PostgresContext.hosts(state.namespace)]

            log(lines_to_tabular(lines, 'NAME,NAMESPACE,ENDPOINT,USERNAME,PASSWORD', separator=','))

    def show_pg_databases(self, pg: PostgresContext):
        log(lines_to_tabular(pg_database_names(pg.namespace, pg.path()), 'DATABASE', separator=','))

    def show_pg_tables(self, pg: PostgresContext):
        log(lines_to_tabular(pg_table_names(pg.namespace, pg.path()), 'NAME', separator=','))

    def cd(self, dir: str, state: ReplState):
        if dir == '':
            state.pg_path = None
        else:
            context: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path, arg=dir)
            # patch up state.namespace from pg cd
            if not state.namespace and context.namespace:
                state.namespace = context.namespace
            state.pg_path = context.path()

    def cd_completion(self, cmd: str, state: ReplState, default: dict = {}):
        pg: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path) if state.pg_path else None
        if pg and pg.db:
            return {cmd: {'..': None}}
        elif pg and pg.host:
            return {cmd: {'..': None} | {p: None for p in pg_database_names(state.namespace, pg.path())}}
        else:
            return {cmd: {p: None for p in PostgresContext.hosts(state.namespace)}}

    def pwd(self, state: ReplState):
        words = []

        pg: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path)

        if pg.host:
            words.append(f'host/{pg.host}')
        if pg.db:
            words.append(f'database/{pg.db}')

        return '\t'.join([f'{ReplState.P}:>'] + (words if words else ['/']))

    def try_fallback_action(self, chain: Command, state: ReplState, cmd: str):
        pg: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path)
        if pg.db:
            return True, chain.run(f'pg {cmd}', state)

        return False, None

    def enter(self, _: ReplState):
        wait_log('Inspecting postgres database instances...')

    def show_tables(self, state: ReplState):
        pg = PostgresContext.apply(state.namespace, state.pg_path)
        lines = [db["name"] for db in pg.tables() if db["schema"] == PostgresContext.default_schema()]
        log(lines_to_tabular(lines, separator=','))

    def show_table_preview(self, state: ReplState, table: str, rows: int):
        PostgresContext.apply(state.namespace, state.pg_path).run_sql(f'select * from {table} limit {rows}')

    def bash(self, s0: ReplState, s1: ReplState, args: list[str]):
        pod, container = PostgresContext.pod_and_container(s1.namespace)
        log2(f'Running on {pod}(container:{container})...')

        return super().bash(s0, s1, args)

    def bash_target_changed(self, s0: ReplState, s1: ReplState):
        return s0.pg_path != s1.pg_path

    def exec_no_dir(self, command: str, state: ReplState):
        with postgres(state) as pod:
            return pod.exec(command, show_out=True)

    def exec_with_dir(self, command: str, session_just_created: bool, state: ReplState):
        with postgres(state) as pod:
            return pod.exec(command, show_out=not session_just_created)

    def bash_completion(self, cmd: str, state: ReplState, default: dict = {}):
        return {cmd: BashCompleter(lambda: [])}