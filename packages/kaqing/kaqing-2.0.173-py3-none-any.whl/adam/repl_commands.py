from adam.commands.alter_tables import AlterTables
from adam.commands.app.app import App
from adam.commands.app.app_ping import AppPing
from adam.commands.app.show_app_actions import ShowAppActions
from adam.commands.app.show_app_id import ShowAppId
from adam.commands.app.show_app_queues import ShowAppQueues
from adam.commands.audit.audit import Audit
from adam.commands.cat import Cat
from adam.commands.code import Code
from adam.commands.deploy.code_start import CodeStart
from adam.commands.deploy.code_stop import CodeStop
from adam.commands.deploy.deploy import Deploy
from adam.commands.deploy.deploy_frontend import DeployFrontend
from adam.commands.deploy.deploy_pg_agent import DeployPgAgent
from adam.commands.deploy.deploy_pod import DeployPod
from adam.commands.deploy.undeploy import Undeploy
from adam.commands.deploy.undeploy_frontend import UndeployFrontend
from adam.commands.deploy.undeploy_pg_agent import UndeployPgAgent
from adam.commands.deploy.undeploy_pod import UndeployPod
from adam.commands.devices.device_app import DeviceApp
from adam.commands.devices.device_auit_log import DeviceAuditLog
from adam.commands.devices.device_cass import DeviceCass
from adam.commands.devices.device_export import DeviceExport
from adam.commands.devices.device_postgres import DevicePostgres
from adam.commands.export.drop_export_database import DropExportDatabase
from adam.commands.export.export import ExportTables
from adam.commands.export.import_session import ImportSession
from adam.commands.export.clean_up_export_sessions import CleanUpExportSessions
from adam.commands.export.clean_up_all_export_sessions import CleanUpAllExportSessions
from adam.commands.export.drop_export_databases import DropExportDatabases
from adam.commands.export.export_select import ExportSelect
from adam.commands.export.export_use import ExportUse
from adam.commands.export.export_select_x import ExportSelectX
from adam.commands.export.show_column_counts import ShowColumnCounts
from adam.commands.export.show_export_databases import ShowExportDatabases
from adam.commands.export.show_export_session import ShowExportSession
from adam.commands.export.show_export_sessions import ShowExportSessions
from adam.commands.kubectl import Kubectl
from adam.commands.shell import Shell
from adam.commands.cp import ClipboardCopy
from adam.commands.bash.bash import Bash
from adam.commands.cd import Cd
from adam.commands.check import Check
from adam.commands.command import Command
from adam.commands.cql.cqlsh import Cqlsh
from adam.commands.exit import Exit
from adam.commands.medusa.medusa import Medusa
from adam.commands.param_get import GetParam
from adam.commands.issues import Issues
from adam.commands.ls import Ls
from adam.commands.nodetool import NodeTool
from adam.commands.postgres.postgres import Postgres, PostgresPg
from adam.commands.preview_table import PreviewTable
from adam.commands.pwd import Pwd
from adam.commands.reaper.reaper import Reaper
from adam.commands.repair.repair import Repair
from adam.commands.report import Report
from adam.commands.restart import Restart
from adam.commands.rollout import RollOut
from adam.commands.param_set import SetParam
from adam.commands.show.show import Show
from adam.commands.show.show_cassandra_status import ShowCassandraStatus
from adam.commands.show.show_cassandra_version import ShowCassandraVersion
from adam.commands.show.show_commands import ShowKubectlCommands
from adam.commands.show.show_host import ShowHost
from adam.commands.show.show_login import ShowLogin
from adam.commands.show.show_params import ShowParams
from adam.commands.show.show_processes import ShowProcesses
from adam.commands.show.show_cassandra_repairs import ShowCassandraRepairs
from adam.commands.show.show_storage import ShowStorage
from adam.commands.show.show_adam import ShowAdam
from adam.commands.watch import Watch

class ReplCommands:
    def repl_cmd_list() -> list[Command]:
        cmds: list[Command] = ReplCommands.navigation() + ReplCommands.cassandra_ops() + ReplCommands.postgres_ops() + \
            ReplCommands.app_ops() + ReplCommands.audit_ops() + ReplCommands.export_ops() + ReplCommands.tools() + ReplCommands.exit()

        intermediate_cmds: list[Command] = [App(), Audit(), Reaper(), Repair(), Deploy(), Show(), Undeploy()]
        ic = [c.command() for c in intermediate_cmds]
        # 1. dedup commands
        deduped = []
        cs = set()
        for cmd in cmds:
            if cmd.command() not in cs and cmd.command() not in ic:
                deduped.append(cmd)
                cs.add(cmd.command())
        # 2. intermediate commands must be added to the end
        deduped.extend(intermediate_cmds)

        # Command.print_chain(Command.chain(cmds))

        return deduped

    def navigation() -> list[Command]:
        return [Ls(), PreviewTable(), DeviceApp(), DevicePostgres(), DeviceCass(), DeviceAuditLog(), DeviceExport(), Cd(), Cat(), Pwd(), ClipboardCopy(),
                GetParam(), SetParam(), ShowParams(), ShowKubectlCommands(), ShowLogin(), ShowAdam(), ShowHost()]

    def cassandra_ops() -> list[Command]:
        return [Cqlsh(), ShowCassandraStatus(), ShowCassandraVersion(), ShowCassandraRepairs(), ShowStorage(), ShowProcesses(),
                Check(), Issues(), NodeTool(), Report(), AlterTables(), Bash(),
                ExportTables(), ExportSelect(), ExportUse(),  ShowExportDatabases(), ShowColumnCounts(),
                DropExportDatabase(), DropExportDatabases(),
                ShowExportSessions(), ShowExportSession(),
                CleanUpExportSessions(), CleanUpAllExportSessions(), ImportSession()] + \
                Medusa().cmd_list() + [Restart(), RollOut(), Watch()] + Reaper().cmd_list() + Repair().cmd_list()

    def postgres_ops() -> list[Command]:
        return [Postgres(), DeployPgAgent(), UndeployPgAgent(), PostgresPg()]

    def app_ops() -> list[Command]:
        return [ShowAppActions(), ShowAppId(), ShowAppQueues(), AppPing(), App()]

    def audit_ops() -> list[Command]:
        return [Audit()] + Audit().cmd_list()

    def export_ops() -> list[Command]:
        return [ExportSelectX(), DropExportDatabase(), DropExportDatabases(), ShowColumnCounts()]

    def tools() -> list[Command]:
        return [Shell(), CodeStart(), CodeStop(), DeployFrontend(), UndeployFrontend(), DeployPod(), UndeployPod(), Kubectl(), Code()]

    def exit() -> list[Command]:
        return [Exit()]