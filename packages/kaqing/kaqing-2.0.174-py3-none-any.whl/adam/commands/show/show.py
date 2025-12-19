import click

from adam.commands.app.show_app_actions import ShowAppActions
from adam.commands.app.show_app_id import ShowAppId
from adam.commands.app.show_app_queues import ShowAppQueues
from adam.commands.intermediate_command import IntermediateCommand
from adam.commands.medusa.medusa_show_backupjobs import MedusaShowBackupJobs
from adam.commands.medusa.medusa_show_restorejobs import MedusaShowRestoreJobs
from adam.commands.show.show_host import ShowHost
from adam.commands.show.show_login import ShowLogin
from .show_params import ShowParams
from .show_cassandra_status import ShowCassandraStatus
from .show_cassandra_version import ShowCassandraVersion
from .show_commands import ShowKubectlCommands
from .show_processes import ShowProcesses
from .show_cassandra_repairs import ShowCassandraRepairs
from .show_storage import ShowStorage
from .show_adam import ShowAdam

class Show(IntermediateCommand):
    COMMAND = 'show'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Show, cls).__new__(cls)

        return cls.instance

    def command(self):
        return Show.COMMAND

    def cmd_list(self):
        return [ShowAppActions(), ShowAppId(), ShowAppQueues(), ShowHost(), ShowLogin(), ShowKubectlCommands(),
                ShowParams(), ShowProcesses(), ShowCassandraRepairs(), ShowStorage(), ShowAdam(),
                ShowCassandraStatus(), ShowCassandraVersion(), MedusaShowRestoreJobs(), MedusaShowBackupJobs()]

class ShowCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        IntermediateCommand.intermediate_help(super().get_help(ctx), Show.COMMAND, Show().cmd_list(), show_cluster_help=True)