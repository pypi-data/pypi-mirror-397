from adam.commands.command import ExtractAllOptionsHandler, ExtractOptionsHandler, ExtractTrailingOptionsHandler
from adam.repl_state import ReplState
from adam.utils_app import AppHandler

def app(state: ReplState) -> AppHandler:
    return AppHandler(state)

def extract_options(args: list[str], options = None):
    return ExtractOptionsHandler(args, options = options)

def extract_trailing_options(args: list[str], trailing = None):
    return ExtractTrailingOptionsHandler(args, trailing = trailing)

def extract_all_options(args: list[str], trailing = None, options = None):
    return ExtractAllOptionsHandler(args, trailing = trailing, options = options)