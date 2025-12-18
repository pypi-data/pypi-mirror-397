from adam.commands.command import Command
from adam.commands.reaper.utils_reaper import reaper
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2

class ReaperRunAbort(Command):
    COMMAND = 'reaper abort run'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperRunAbort, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperRunAbort.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            if not args:
                if state.in_repl:
                    log2('Specify run id to abort.')
                else:
                    Command.display_help()

                return state

            with reaper(state) as requests:
                requests.put(f'repair_run/{args[0]}/state/ABORTED')

            return state

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperRunAbort.COMMAND} <run-id>\t abort reaper run'