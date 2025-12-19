"""Editor widget central to the application"""

from . import bindings

from textual.widgets           import TextArea
from textual.widgets.text_area import Edit
from textual.reactive          import reactive
from textual.message           import Message
from textual.events            import Key
from textual.events            import MouseDown

import tokenize
from pathlib import Path


class Editor(TextArea, inherit_bindings=False):
    """Widget for editing a file."""

    file: reactive[Path | None] = reactive(None)
    """The file being edited."""

    encoding: str = ''
    """The detected text encoding of the file."""

    newline: str = ''
    """The character sequence marking line endings in the file."""

    saved_as: list[list[Edit]] = None
    """The undo stack when the file was last save or first loaded."""

    class FileLoaded(Message):
        """Message posted when a file was loaded."""

    class EncodingDetected(Message):
        """Message posted when text encoding was detected."""

    class NewlineDetected(Message):
        """Message posted when line endings were detected."""

    class CursorMoved(Message):
        """Message posted when cursor was moved."""

    BINDINGS = bindings.editor

    DEFAULT_CSS = """
        Editor {
            border:  round $primary;
            padding: 0;
        }
    """

    def __init__(self, id: str = 'editor'):
        self.log('Initializing editor widget.')
        super().__init__(
            id                = id,
            soft_wrap         = False,
            tab_behavior      = 'indent',
            show_line_numbers = False,
            max_checkpoints   = 1000,
            theme             = 'css',
        )

    def watch_file(self, file: Path | None):
        """Loads file whenever the reactive `file` attribute changes."""

        if file is None:
            self.log('Editor widget waiting for a file to load.')
            return
        self.log(f'Loading file "{file}" into editor widget.')

        language = infer_language(file)
        self.log(f'Inferred language is "{language}".')
        if language in self.available_languages:
            self.language = language
        else:
            self.log('Inferred language not available.')
            self.language = None

        encoding = detect_encoding(file)
        self.log(f'Detected encoding "{encoding}".')
        self.encoding = encoding
        self.post_message(self.EncodingDetected())

        with file.open(encoding=self.encoding) as stream:
            self.load_text(stream.read())
            newlines = stream.newlines

        if not isinstance(newlines, str):
            self.app.exit('File contains mixed line endings.', return_code=11)
        self.log(f'Detected line endings "{newlines!r}".')
        self.newline = newlines
        self.post_message(self.NewlineDetected())

        self.file = file
        self.post_message(self.FileLoaded())
        self.saved_as = self.history.undo_stack.copy()
        self.post_message(self.CursorMoved())

    def on_key(self, _event: Key):
        """Event triggered when the user presses a key."""
        self.post_message(self.CursorMoved())

    def on_mouse_up(self, _event: MouseDown):
        """Event triggered when the user releases a mouse button."""
        self.post_message(self.CursorMoved())

    def on_text_area_changed(self):
        """Event triggered when the user modified the text."""
        self.refresh_bindings()

    def action_save(self):
        """Saves the file to disk."""
        if not self.file:
            return
        self.log(f'Saving file "{self.file}" with encoding {self.encoding}.')
        self.file.write_text(
            self.text, encoding=self.encoding, newline=self.newline
        )
        self.saved_as = self.history.undo_stack.copy()
        self.refresh_bindings()

    def action_trim_whitespace(self):
        """Trims trailing white-space characters."""
        self.log('Trimming trailing white-space characters.')
        self.notify('Trimming white-space has yet to be implemented.')

    def action_toggle_wrapping(self):
        """Toggles the soft-wrapping of lines."""
        self.log('Toggling soft-wrapping of lines.')
        self.soft_wrap = not self.soft_wrap

    def check_action(self, action: str, _: tuple[object, ...]) -> bool | None:
        """Marks actions as currently available or not."""
        if action == 'save' and self.file and not self.modified:
            return None
        return True

    @property
    def modified(self):
        """Returns whether the file has been modified since it was saved."""
        return (self.history.undo_stack != self.saved_as)


def detect_encoding(file: Path) -> str:
    """
    Detects the text encoding of the given file.

    Uses the `tokenize` module from the Python standard library under the hood,
    and is thus limited to the same encodings.
    """
    with file.open('rb') as stream:
        (encoding, _line) = tokenize.detect_encoding(stream.readline)
    return encoding


def infer_language(file: Path) -> str:
    """Infers the syntax-highlighting language from the file extension."""
    match file.suffix:
        case '.md':
            return 'markdown'
        case '.json':
            return 'json'
        case '.yaml' | '.yml':
            return 'yaml'
        case '.toml':
            return 'toml'
        case '.xml':
            return 'xml'
        case '.html' | '.htm':
            return 'html'
        case '.css':
            return 'css'
        case '.js':
            return 'javascript'
        case '.sh' | '.bash' | '.zsh':
            return 'bash'
        case '.py' | '.pyw':
            return 'python'
        case '.rs':
            return 'rust'
        case '.sql':
            return 'sql'
        case '.go':
            return 'go'
        case '.java':
            return 'java'
        case '.kt' | '.kts':
            return 'kotlin'
        case _:
            return ''
