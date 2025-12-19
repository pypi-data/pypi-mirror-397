import click
import pyperclip

from adam.commands import validate_args
from adam.commands.command import Command, InvalidArgumentsException
from adam.commands.command_helpers import ClusterOrPodCommandHelper
from adam.commands.cli_commands import CliCommands
from adam.repl_state import ReplState, RequiredState
from adam.utils import lines_to_tabular, log, log2

class ClipboardCopy(Command):
    COMMAND = 'cp'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ClipboardCopy, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ClipboardCopy.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            def display_keys():
                log2('Key is required.')
                log2()
                log2('Keys:')
                log2(lines_to_tabular([f'{k},{v}' for k, v in CliCommands.values(state, collapse=True).items()], separator=','))

            with validate_args(args, state, name='key', msg=display_keys) as key:
                if not key in CliCommands.values(state):
                    if state.in_repl:
                        display_keys()
                    else:
                        log2('* Invalid key')
                        Command.display_help()

                    raise InvalidArgumentsException()

                value = CliCommands.values(state)[key]
                pyperclip.copy(value)
                log2('The following line has been copied to clipboard. Use <Ctrl-V> to use it.')
                log2(f'  {value}')

                return state

    def completion(self, state: ReplState):
        return super().completion(state, lambda: {key: None for key in CliCommands.values(state).keys()})

    def help(self, _: ReplState):
        return f"{ClipboardCopy.COMMAND} <key>\t copy a value to clipboard for conveninence"

class CopyCommandHelper(click.Command):
    def lines(self):
        return [
            'node-exec-?: kubectl exec command to the Cassandra pod',
            'reaper-exec: kubectl exec command to the Reaper pod',
            'reaper-forward: kubectl port-forward command to the Reaper pod',
            'reaper-ui: uri to Reaper ui',
            'reaper-username: Reaper user name',
            'reaper-password: Reaper password',
        ]

    def get_help(self, ctx: click.Context):
        log(super().get_help(ctx))
        log()
        log('Keys:')

        log(lines_to_tabular(self.lines(), separator=':'))
        log()
        ClusterOrPodCommandHelper.cluter_or_pod_help()