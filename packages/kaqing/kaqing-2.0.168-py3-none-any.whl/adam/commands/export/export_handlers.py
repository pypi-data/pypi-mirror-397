from adam.commands.command import Command
from adam.commands.export.export_databases import ExportDatabases
from adam.commands.export.exporter import Exporter
from adam.commands.export.utils_export import ExportSpec, state_with_pod
from adam.repl_state import ReplState
from adam.utils import log, log2

class ExporterHandler:
    def __init__(self, state: ReplState, export_only=False):
        self.state = state
        self.export_only = export_only

    def __enter__(self):
        return self.exec

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def exec(self, args: list[str]):
        state = self.state
        export_only = self.export_only
        export_session = state.export_session
        spec: ExportSpec = None
        try:
            with state_with_pod(state) as state:
                # --export-only for testing only
                statuses, spec = Exporter.export_tables(args, state, export_only=export_only)
                if not statuses:
                    return state

                Exporter.clear_export_session_cache()

                if spec.importer == 'csv' or export_only:
                    ExportDatabases.disply_export_session(state.sts, state.pod, state.namespace, spec.session)
                else:
                    log()
                    ExportDatabases.display_export_db(state.export_session)
        finally:
            # if exporting to csv, do not bind the new session id to repl state
            if spec and spec.importer == 'csv':
                state.export_session = export_session

        return state

def exporter(state: ReplState, export_only=False):
    return ExporterHandler(state, export_only=export_only)

class ImporterHandler:
    def __init__(self, state: ReplState):
        self.state = state

    def __enter__(self):
        return self.exec

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state.pop()

        return False

    def exec(self, args: list[str]):
        state = self.state

        if not args:
            if state.in_repl:
                log2('Specify export session name.')
            else:
                log2('* Export session name is missing.')

                Command.display_help()

            return 'command-missing'

        with state_with_pod(state) as state:
            tables, _ = Exporter.import_session(args, state)
            if tables:
                Exporter.clear_export_session_cache()

                log()
                ExportDatabases.display_export_db(state.export_session)

        return state

def importer(state: ReplState):
    return ImporterHandler(state)