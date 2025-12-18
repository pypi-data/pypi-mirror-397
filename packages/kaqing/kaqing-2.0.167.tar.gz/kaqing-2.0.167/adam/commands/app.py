from adam.commands import app_rest
from adam.commands.command import Command
from adam.repl_state import ReplState, RequiredState

class App(Command):
    COMMAND = 'app'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(App, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return App.COMMAND

    def required(self):
        return RequiredState.APP_APP

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state, options='--force') as (args, state, forced):
            with app_rest(state, forced=forced) as post:
                post(args)

            return state

    def completion(self, state: ReplState):
        if state.app_app:
            return super().completion(state, {'--force': None})

        return {}

    def help(self, _: ReplState):
        return f"<AppType>.<AppAction> <args> [--force]\t post app action; check with 'show app actions' command"