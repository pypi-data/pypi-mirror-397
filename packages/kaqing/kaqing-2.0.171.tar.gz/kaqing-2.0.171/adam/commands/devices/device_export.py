from adam.commands.command import Command
from adam.commands.devices.device import Device
from adam.commands.export.export_databases import ExportDatabases
from adam.config import Config
from adam.repl_state import ReplState
from adam.utils import lines_to_tabular, log, log2, wait_log

class DeviceExport(Command, Device):
    COMMAND = f'{ReplState.X}:'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(DeviceExport, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return DeviceExport.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        state.device = ReplState.X

        return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{DeviceExport.COMMAND}\t move to Export Database Operations device'

    def ls(self, cmd: str, state: ReplState):
        if state.export_session:
            self.show_export_tables(state.export_session)
        else:
            self.show_export_databases()

    def show_export_databases(self, importer: str = None):
        lines = [f'{k}\t{v}' for k, v in ExportDatabases.database_names_with_keyspace_cnt(importer).items()]
        log(lines_to_tabular(lines, 'NAME\tKEYSPACES', separator='\t'))

    def show_export_tables(self, export_session: str):
        log(lines_to_tabular(ExportDatabases.table_names(export_session), 'NAME', separator=','))

    def cd(self, dir: str, state: ReplState):
        if dir in ['', '..']:
            state.export_session = None
        else:
            state.export_session = dir

    def cd_completion(self, cmd: str, state: ReplState, default: dict = {}):
        if state.export_session:
            return {cmd: {'..': None} | {n: None for n in ExportDatabases.database_names()}}
        else:
            return {cmd: {n: None for n in ExportDatabases.database_names()}}

    def pwd(self, state: ReplState):
        words = []

        if state.export_session:
            words.append(state.export_session)

        return '\t'.join([f'{ReplState.X}:>'] + (words if words else ['/']))

    def try_fallback_action(self, chain: Command, state: ReplState, cmd: str):
        result = chain.run(f'.{cmd}', state)
        if type(result) is ReplState:
            if state.export_session and not result.export_session:
                state.export_session = None

        return True, result

    def enter(self, state: ReplState):
        if auto_enter := Config().get('repl.x.auto-enter', 'no'):
            if auto_enter == 'latest':
                wait_log(f'Moving to the latest export database...')
                if dbs := ExportDatabases.database_names():
                    state.export_session = sorted(dbs)[-1]
                else:
                    log2('No export database found.')

