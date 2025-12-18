from adam.commands import extract_options
from adam.commands.command import Command
from adam.commands.commands_utils import show_table
from adam.commands.cql.utils_cql import cassandra
from adam.config import Config
from adam.utils_k8s.statefulsets import StatefulSets
from adam.repl_state import ReplState, RequiredState

class ShowProcesses(Command):
    COMMAND = 'show processes'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowProcesses, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowProcesses.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            with extract_options(args, ['-s', '--show']) as (args, show_out):
                cols = Config().get('processes.columns', 'pod,cpu-metrics,mem')
                header = Config().get('processes.header', 'POD_NAME,M_CPU(USAGE/LIMIT),MEM/LIMIT')

                qing_args = ['qing', 'recipe', 'with']
                args, _, recipe_qing = Command.extract_options(args, options=qing_args)
                if set(recipe_qing) == set(qing_args):
                    cols = Config().get('processes-qing.columns', 'pod,cpu,mem')
                    header = Config().get('processes-qing.header', 'POD_NAME,Q_CPU/TOTAL,MEM/LIMIT')

                with cassandra(state) as pods:
                    pods.show_table(cols, header, show_out=show_out)

                return state

    def completion(self, state: ReplState):
        return super().completion(state, {'with': {'recipe': {'metrics': {'-s': None}, 'qing': {'-s': None}}}, '-s': None})

    def help(self, _: ReplState):
        return f'{ShowProcesses.COMMAND} [with recipe qing|metrics] [-s]\t show process overview  -s show commands on nodes'