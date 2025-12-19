import click

from adam.commands import extract_trailing_options, validate_args
from adam.commands.command import Command
from adam.commands.intermediate_command import IntermediateCommand
from adam.commands.postgres.psql_completions import psql_completions
from adam.commands.postgres.utils_postgres import pg_table_names, postgres
from .postgres_ls import PostgresLs
from .postgres_preview import PostgresPreview
from .postgres_context import PostgresContext
from adam.repl_state import ReplState
from adam.utils import log, log2

class Postgres(IntermediateCommand):
    COMMAND = 'pg'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Postgres, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Postgres.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with extract_trailing_options(args, '&') as (args, backgrounded):
                with validate_args(args, state, name='SQL statement') as sql:
                    if not state.pg_path:
                        if state.in_repl:
                            log2('Enter "use <pg-name>" first.')
                        else:
                            log2('* pg-name is missing.')

                        return state

                    if state.in_repl:
                        with postgres(state) as pod:
                            pod.sql(args, background=backgrounded)
                    elif not self.run_subcommand(cmd, state):
                        with postgres(state) as pod:
                            pod.sql(args, background=backgrounded)

                    return state

    def cmd_list(self):
        return [PostgresLs(), PostgresPreview(), PostgresPg()]

    def completion(self, state: ReplState):
        if state.device != state.P:
            # conflicts with cql completions
            return {}

        leaf = {}
        session = PostgresContext.apply(state.namespace, state.pg_path)
        if session.db:
          if pg_table_names(state.namespace, state.pg_path):
            leaf = psql_completions(state.namespace, state.pg_path)
        elif state.pg_path:
            leaf = {
                '\h': None,
                '\l': None,
            }

        if state.pg_path:
            return super().completion(state, leaf) | leaf
        else:
            return {}

    def help(self, _: ReplState):
        return f'<sql-statements> [&]\t run queries on Postgres databases'

class PostgresCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        IntermediateCommand.intermediate_help(super().get_help(ctx), Postgres.COMMAND, Postgres().cmd_list(), show_cluster_help=True)
        log('PG-Name:  Kubernetes secret for Postgres credentials')
        log('          e.g. stgawsscpsr-c3-c3-k8spg-cs-001')
        log('Database: Postgres database name within a host')
        log('          e.g. stgawsscpsr_c3_c3')

# No action body, only for a help entry and auto-completion
class PostgresPg(Command):
    COMMAND = 'pg'

    def command(self):
        return PostgresPg.COMMAND

    def help(self, _: ReplState):
        return f'pg <sql-statements>\t run queries on Postgres databases'