from adam.commands import extract_options
from adam.commands.command import Command
from adam.commands.cql.utils_cql import cassandra
from adam.config import Config
from adam.repl_state import ReplState, RequiredState

class ShowStorage(Command):
    COMMAND = 'show storage'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowStorage, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowStorage.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with extract_options(args, ['-s', '--show']) as (args, show_out):
                cols = Config().get('storage.columns', 'pod,volume_root,volume_cassandra,snapshots,data,compactions')
                header = Config().get('storage.header', 'POD_NAME,VOLUME /,VOLUME CASS,SNAPSHOTS,DATA,COMPACTIONS')
                with cassandra(state) as pods:
                    pods.display_table(cols, header, show_out=show_out)

                return state

    def completion(self, state: ReplState):
        return super().completion(state, {'-s': None})

    def help(self, _: ReplState):
        return f'{ShowStorage.COMMAND} [-s]\t show storage overview  -s show commands on nodes'