from abc import abstractmethod

from adam.commands.command import Command
from adam.config import Config
from adam.pod_exec_result import PodExecResult
from adam.repl_state import BashSession, ReplState
from adam.utils import log2

class Device:
    @abstractmethod
    def ls(self, cmd: str, state: ReplState):
        pass

    def ls_completion(self, cmd: str, state: ReplState, default: dict = {}):
        return default

    @abstractmethod
    def cat(self, cmd: str, state: ReplState):
        pass

    def cat_completion(self, cmd: str, state: ReplState, default: dict = {}):
        return default

    def cd(self, dir: str, state: ReplState):
        pass

    def cd_completion(self, cmd: str, state: ReplState, default: dict = {}):
        return default

    @abstractmethod
    def pwd(self, state: ReplState):
        pass

    def try_fallback_action(self, chain: Command, state: ReplState, cmd: str):
        return False, None

    def enter(self, state: ReplState):
        pass

    def preview(self, table: str, state: ReplState):
        if not table:
            if state.in_repl:
                log2('Table is required.')
                log2()
                log2('Tables:')
                self.show_tables(state)
            else:
                log2('* Table is missing.')
                self.show_tables(state)

                Command.display_help()

            return 'command-missing'

        rows = Config().get('preview.rows', 10)
        self.show_table_preview(state, table, rows)

        return state

    @abstractmethod
    def show_tables(self, state: ReplState):
        pass

    @abstractmethod
    def show_table_preview(self, state: ReplState, table: str, rows: int):
        pass

    def bash(self, s0: ReplState, s1: ReplState, args: list[str]):
        if s1.in_repl:
            if self.bash_target_changed(s0, s1):
                r = self._exec_with_dir(s1, args)
            else:
                r = self._exec_with_dir(s0, args)

            if not r:
                s1.exit_bash()

                return 'inconsistent pwd'

            return r
        else:
            self.exec_no_dir(' '.join(args), s1)

            return s1

    def _exec_with_dir(self, state: ReplState, args: list[str]) -> list[PodExecResult]:
        session_just_created = False
        if not args:
            session_just_created = True
            session = BashSession(state.device)
            state.enter_bash(session)

        if state.bash_session:
            if args != ['pwd']:
                if args:
                    args.append('&&')
                args.extend(['pwd', '>', f'/tmp/.qing-{state.bash_session.session_id}'])

            if not session_just_created:
                if pwd := state.bash_session.pwd(state):
                    args = ['cd', pwd, '&&'] + args

        return self.exec_with_dir(' '.join(args), session_just_created, state)

    @abstractmethod
    def bash_target_changed(self, s0: ReplState, s1: ReplState):
        pass

    @abstractmethod
    def exec_no_dir(self, command: str, state: ReplState):
        pass

    @abstractmethod
    def exec_with_dir(self, command: str, session_just_created: bool, state: ReplState):
        pass

    def bash_completion(self, cmd: str, state: ReplState, default: dict = {}):
        return default