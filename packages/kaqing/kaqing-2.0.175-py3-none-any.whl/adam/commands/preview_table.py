from adam.commands.command import Command
from adam.commands.devices.devices import Devices
from adam.repl_state import ReplState, RequiredState

class PreviewTable(Command):
    COMMAND = 'preview'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(PreviewTable, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return PreviewTable.COMMAND

    def required(self):
        return [RequiredState.CLUSTER_OR_POD, RequiredState.PG_DATABASE, ReplState.L, RequiredState.EXPORT_DB]

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validate(args, state) as (args, state):
            Devices.device(state).preview(args[0] if args else None, state)

            return state

    def completion(self, _: ReplState):
        # taken care of by the sql completer
        return {}

    def help(self, _: ReplState):
        return f'{PreviewTable.COMMAND} TABLE\t preview table'