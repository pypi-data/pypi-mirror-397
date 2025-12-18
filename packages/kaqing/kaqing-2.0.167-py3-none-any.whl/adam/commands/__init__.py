from adam.commands.cql.utils_cql import CqlShHandler
from adam.repl_state import ReplState
from adam.utils_app import AppExecHandler, AppRestHandler

def cqlsh(state: ReplState, opts: list = [], show_out = False, show_query = False, use_single_quotes = False, on_any = False, background = False) -> CqlShHandler:
    return CqlShHandler(state, opts = opts, show_out = show_out, show_query = show_query, use_single_quotes = use_single_quotes, on_any = on_any, background=background)

def app(state: ReplState, show_out = True) -> AppExecHandler:
    return AppExecHandler(state, show_out = show_out)

def app_rest(state: ReplState, forced = False) -> AppRestHandler:
    return AppRestHandler(state, forced = forced)