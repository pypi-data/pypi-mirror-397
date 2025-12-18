from adam.commands import app_rest
from adam.commands.command import Command
from adam.repl_state import ReplState, RequiredState

class ShowAppQueues(Command):
    COMMAND = 'show app queues'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowAppQueues, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowAppQueues.COMMAND

    def required(self):
        return RequiredState.APP_APP

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state, options='--force') as (_, state, forced):
            with app_rest(state, forced=forced) as post:
                post(['InvalidationQueue.countAll'])

            return state

    def completion(self, state: ReplState):
        if state.app_app:
            return super().completion(state, {'--force': None})

        return {}

    def help(self, _: ReplState):
        return f"{ShowAppQueues.COMMAND} [--force]\t show invalidation queue counts"