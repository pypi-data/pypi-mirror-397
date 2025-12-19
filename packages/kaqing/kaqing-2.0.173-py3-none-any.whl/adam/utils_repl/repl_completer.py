import re
from typing import Iterable, TypeVar
from prompt_toolkit.completion import CompleteEvent, Completion, NestedCompleter, WordCompleter
from prompt_toolkit.document import Document

__all__ = [
    "ReplCompleter",
]

T = TypeVar('T')

class ReplCompleter(NestedCompleter):
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # If there is a space, check for the first term, and use a
        # subcompleter.
        if " " in text:
            first_term = text.split()[0]
            completer = self.options.get(first_term)

            # If we have a sub completer, use this for the completions.
            if completer is not None:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                for c in completer.get_completions(new_document, complete_event):
                    yield c

        # No space in the input: behave exactly like `WordCompleter`.
        else:
            completer = WordCompleter(
                # Allow dot in the middle or a word
                list(self.options.keys()), ignore_case=self.ignore_case, pattern=re.compile(r"([a-zA-Z0-9_\.\@\&]+|[^a-zA-Z0-9_\.\@\&\s]+)")
            )
            for c in completer.get_completions(document, complete_event):
                yield c