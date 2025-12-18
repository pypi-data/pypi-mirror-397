from adam.commands.command import Command
from adam.commands.reaper.utils_reaper import Reapers, reaper
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2

class ReaperScheduleStop(Command):
    COMMAND = 'reaper stop schedule'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperScheduleStop, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperScheduleStop.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        with self.validating(args, state) as (args, state):
            if not args:
                log2('Specify run schedule to stop.')

                return state

            with reaper(state) as requests:
                schedule_id = args[0]
                requests.put(f'repair_schedule/{schedule_id}?state=PAUSED')
                Reapers.show_schedule(state, schedule_id)

            return schedule_id

    def completion(self, state: ReplState):
        if state.sts:
            leaf = {id: None for id in Reapers.cached_schedule_ids(state)}

            return super().completion(state, leaf)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperScheduleStop.COMMAND} <schedule-id>\t pause reaper schedule'