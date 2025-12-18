from adam.commands.command import Command
from adam.commands.devices.device import Device
from adam.commands.devices.devices import Devices
from adam.repl_state import ReplState

class Cd(Command):
    COMMAND = 'cd'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Cd, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Cd.COMMAND

    def required(self):
        return ReplState.NON_L

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state, apply=False) as (args, state):
            if len(args) < 2:
                return state

            device: Device = Devices.device(state)
            arg = args[1]
            for dir in arg.split('/'):
                device.cd(dir, state)

            return state

    def completion(self, state: ReplState):
        return Devices.device(state).cd_completion(Cd.COMMAND, state, default = {})

    def help(self, _: ReplState):
        return f'{Cd.COMMAND} <path> | .. \t move around on the operational device hierarchy'