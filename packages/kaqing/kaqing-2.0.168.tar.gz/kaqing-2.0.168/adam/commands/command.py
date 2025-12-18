from abc import abstractmethod
import copy
import subprocess
import sys
from typing import Union

from adam.commands.command_helpers import ClusterCommandHelper
from adam.repl_state import ReplState, RequiredState
from adam.utils import is_lambda, lines_to_tabular, log, log2

repl_cmds: list['Command'] = []

class Command:
    """Abstract base class for commands"""
    def __init__(self, successor: 'Command'=None):
        if not hasattr(self, '_successor'):
            self._successor = successor

    @abstractmethod
    def command(self) -> str:
        pass

    # The chain of responsibility pattern
    # Do not do child of child!!!
    @abstractmethod
    def run(self, cmd: str, state: ReplState):
        if self._successor:
            return self._successor.run(cmd, state)

        return None

    def completion(self, state: ReplState, leaf: dict[str, any] = None) -> dict[str, any]:
        if not self.validate_state(state, show_err=False):
            return {}

        if is_lambda(leaf):
            leaf = leaf()

        d = leaf
        for t in reversed(self.command().split(' ')):
            d = {t: d}

        return d

    def required(self) -> RequiredState:
        return None

    def validating(self, args: list[str], state: ReplState, apply = True, options = None):
        return ValidateHandler(self, args, state, apply = apply, options = options)

    def validate_state(self, state: ReplState, show_err = True):
        return state.validate(self.required(), show_err=show_err)

    def help(self, _: ReplState) -> str:
        return None

    def args(self, cmd: str):
        a = list(filter(None, cmd.split(' ')))
        spec = self.command_tokens()
        if spec != a[:len(spec)]:
            return None

        return a

    def apply_state(self, args: list[str], state: ReplState, resolve_pg = True, args_to_check = 6) -> tuple[ReplState, list[str]]:
        """
        Applies any contextual arguments such as namespace or statefulset to the ReplState and returns any non-contextual arguments.
        """
        return state.apply_args(args, cmd=self.command_tokens(), resolve_pg=resolve_pg, args_to_check=args_to_check)

    def command_tokens(self):
        return self.command().split(' ')

    # build a chain-of-responsibility chain
    def chain(cl: list['Command']):
        global repl_cmds
        repl_cmds.extend(cl)

        cmds = cl[0]
        cmd = cmds
        for successor in cl[1:]:
            cmd._successor = successor
            cmd = successor

        return cmds

    def command_to_completion(self):
        # COMMAND = 'reaper activate schedule'
        d = None
        for t in reversed(self.command().split(' ')):
            d = {t: d}

        return d

    def display_help():
        args = copy.copy(sys.argv)
        args.extend(['--help'])
        subprocess.run(args)

    def extract_options(args: list[str], names: list[str]):
        found: list[str] = []

        new_args: list[str] = []
        for arg in args:
            if arg in names:
                found.append(arg)
            else:
                new_args.append(arg)

        return new_args, found

    def print_chain(cmd: 'Command'):
        print(f'{cmd.command()}', end = '')
        while s := cmd._successor:
            print(f'-> {s.command()}', end = '')
            cmd = s
        print()

class InvalidState(Exception):
    def __init__(self, state: ReplState):
        super().__init__(f'Invalid state')

class ValidateHandler:
    def __init__(self, cmd: Command, args: list[str], state: ReplState, apply = True, options = None):
        self.cmd = cmd
        self.args = args
        self.state = state
        self.apply = apply
        self.options = options

    def __enter__(self) -> Union[tuple[list[str], ReplState], tuple[list[str], ReplState, list[str]]]:
        state = self.state
        args = self.args
        if self.apply:
            state, args = self.cmd.apply_state(args, state)

        if not self.cmd.validate_state(state):
            raise InvalidState(state)

        if self.options:
            args, options = Command.extract_options(args, self.options)
            return args, state, options

        return args, state

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False