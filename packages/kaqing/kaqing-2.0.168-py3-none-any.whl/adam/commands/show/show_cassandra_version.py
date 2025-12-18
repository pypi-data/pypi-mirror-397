from adam.commands import cqlsh
from adam.commands.command import Command
from adam.repl_state import ReplState, RequiredState

class ShowCassandraVersion(Command):
    COMMAND = 'show cassandra version'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowCassandraVersion, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowCassandraVersion.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (_, state):
            with cqlsh(state, show_out=True, on_any=True) as query:
                return query('show version')

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ShowCassandraVersion.COMMAND}\t show Cassandra version'