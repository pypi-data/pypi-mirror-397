from adam.commands.command import Command
from adam.repl_state import ReplState, RequiredState
from adam.utils_k8s.k8s import nodetool

class ShowCassandraRepairs(Command):
    COMMAND = 'show cassandra repairs'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowCassandraRepairs, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowCassandraRepairs.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            with nodetool(state) as exec:
                return exec('repair_admin list')

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ShowCassandraRepairs.COMMAND}\t show Cassandra repairs'