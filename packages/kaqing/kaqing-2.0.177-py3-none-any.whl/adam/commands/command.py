from abc import abstractmethod
from collections.abc import Callable
import copy
import subprocess
import sys
from typing import Union

from adam.repl_state import ReplState, RequiredState
from adam.utils import is_lambda, log2

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

    def validate(self, args: list[str], state: ReplState, apply = True):
        return ValidateStateHandler(self, args, state, apply = apply)

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

    def extract_options(args: list[str], trailing: Union[str, list[str]] = [], sequence: list[str] = [], options: list[str] = []):
        found_options: list[str] = []
        found_trailing = None
        found_sequence = None

        if trailing is None:
            trailing = []
        elif isinstance(trailing, str):
            trailing = [trailing]

        if options is None:
            options = []
        elif isinstance(options, str):
            options = [options]

        if args and trailing:
            while args[-1] in trailing:
                found_trailing = True
                args = args[:-1]

        if args and sequence:
            args, found_sequence = Command.extract_option_sequence(args, sequence)

        new_args: list[str] = []
        if args:
            for arg in args:
                if arg in options:
                    found_options.append(arg)
                else:
                    new_args.append(arg)

        return new_args, found_trailing, found_sequence, found_options

    def extract_option_sequence(args, sequence):
        len_sub = len(sequence)
        len_main = len(args)
        for i in range(len_main - len_sub + 1):
            if args[i:i+len_sub] == sequence:
                new_args = copy.copy(args)
                del new_args[i:i+len_sub]

                return new_args, True

        return new_args, False

    def print_chain(cmd: 'Command'):
        print(f'{cmd.command()}', end = '')
        while s := cmd._successor:
            print(f'-> {s.command()}', end = '')
            cmd = s
        print()

class InvalidStateException(Exception):
    def __init__(self, state: ReplState):
        super().__init__(f'Invalid state')

class ValidateStateHandler:
    def __init__(self, cmd: Command, args: list[str], state: ReplState, apply = True):
        self.cmd = cmd
        self.args = args
        self.state = state
        self.apply = apply

    def __enter__(self) -> tuple[list[str], ReplState]:
        state = self.state
        args = self.args
        if self.apply:
            state, args = self.cmd.apply_state(args, state)
        else:
            args = args[len(self.cmd.command_tokens()):]

        if not self.cmd.validate_state(state):
            raise InvalidStateException(state)

        return args, state

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

class InvalidArgumentsException(Exception):
    def __init__(self):
        super().__init__(f'Invalid arguments')

class ValidateArgCountHandler:
    def __init__(self, args: list[str], state: ReplState, count_at_least: int = 1, name: str = None, msg: Callable[[], None] = None, default: Union[str, list[str]] = None):
        self.args = args
        self.state = state
        self.count_at_least = count_at_least
        self.name = name
        self.msg = msg
        self.default = default

    def __enter__(self) -> tuple[list[str], ReplState]:
        if len(self.args) < self.count_at_least:
            if self.default:
                v = self.default
                if isinstance(v, list):
                    v = ' '.join(v)

                return v

            if self.state.in_repl:
                if self.msg:
                    self.msg()
                elif self.name:
                    log2(f'{self.name} is required.')
            elif self.name:
                log2(f'* {self.name} is missing.')

                Command.display_help()

            raise InvalidArgumentsException()

        return ' '.join(self.args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

class ExtractOptionsHandler:
    def __init__(self, args: list[str], options: list[str] = None):
        self.args = args
        self.options = options

    def __enter__(self) -> tuple[list[str], list[str]]:
        args, _, _, options = Command.extract_options(self.args, options=self.options)
        return args, options

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

class ExtractTrailingOptionsHandler:
    def __init__(self, args: list[str], trailing: list[str] = None):
        self.args = args
        self.trailing = trailing

    def __enter__(self) -> tuple[list[str], list[str]]:
        args, trailing, _, _ = Command.extract_options(self.args, trailing=self.trailing)
        return args, trailing

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

class ExtractAllOptionsHandler:
    def __init__(self, args: list[str], trailing: list[str] = None, sequence: list[str] = None, options: list[str] = None):
        self.args = args
        self.trailing = trailing
        self.sequence = sequence
        self.options = options

    def __enter__(self) -> tuple[list[str], list[str]]:
        return Command.extract_options(self.args, trailing=self.trailing, sequence=self.sequence, options=self.options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

class ExtractSequenceOptionsHandler:
    def __init__(self, args: list[str], sequence: list[str]):
        self.args = args
        self.sequence = sequence

    def __enter__(self) -> tuple[list[str], list[str]]:
        args, _, sequence, _ = Command.extract_options(self.args, sequence=self.sequence)
        return args, sequence

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
