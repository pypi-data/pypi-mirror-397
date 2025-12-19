"""Text-based user interface of the application"""

from .          import meta
from .          import bindings
from .          import dialogs
from .editor    import Editor
from .statusbar import Statusbar

from textual.app       import App
from textual.app       import ComposeResult
from textual.app       import SystemCommand
from textual.binding   import Binding
from textual.reactive  import reactive
from textual.screen    import Screen

from pathlib         import Path
from collections.abc import Iterable


class TUI(App[str], inherit_bindings=False):
    """Text-based user interface"""

    file: reactive[Path | None] = reactive(None)
    """The file being edited."""

    encoding: reactive[str] = reactive('')
    """The text encoding of the file."""

    newline: reactive[str] = reactive('')
    """The line endings of the file."""

    cursor: reactive[tuple[int, int]] = reactive((1, 1))
    """The current cursor position."""

    BINDINGS = bindings.application
    CSS_PATH = 'tui.tcss'

    def compose(self) -> ComposeResult:
        """Composes the application's user interface."""
        self.log('Composing application interface.')
        yield Editor(id='editor').data_bind(file=TUI.file)
        yield Statusbar(id='statusbar').data_bind(
            file     = TUI.file,
            encoding = TUI.encoding,
            newline  = TUI.newline,
            cursor   = TUI.cursor,
        )

    def get_key_display(self, binding: Binding) -> str:
        """Shows key bindings in upper case, not the default lower case."""
        return super().get_key_display(binding).upper()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Populates command palette."""
        commands = []
        commands.append((
            'Quit',
            'Quit the application.',
            'quit',
            self.action_quit,
        ))
        if screen.query('HelpPanel'):
            commands.append((
                'Keys',
                'Hide help panel with key bindings.',
                'hide_help_panel',
                self.action_hide_help_panel,
            ))
        else:
            commands.append((
                'Keys',
                'Show help panel with key bindings.',
                'show_help_panel',
                self.action_show_help_panel,
            ))
        commands.append((
            'Theme',
            'Change the application theme.',
            'change_theme',
            self.action_change_theme,
        ))
        commands.append((
            'Screenshot',
            'Save SVG image of screen in current folder.',
            'screenshot',
            lambda: self.set_timer(0.1, self.action_screenshot),
        ))
        actions_to_bindings = {
            binding.action: binding
            for (_, binding, enabled, _) in screen.active_bindings.values()
            if enabled
        }
        for (title, help, action, callback) in commands:
            if binding := actions_to_bindings.get(action):
                key = self.get_key_display(binding)
                title += f' ({key})'
            yield SystemCommand(title=title, help=help, callback=callback)

    def on_editor_encoding_detected(self):
        """Event triggered when editor detected the text encoding."""
        editor = self.query_exactly_one('#editor', expect_type=Editor)
        self.encoding = editor.encoding

    def on_editor_newline_detected(self):
        """Event triggered when editor detected the line endings."""
        editor = self.query_exactly_one('#editor', expect_type=Editor)
        self.newline = editor.newline

    def on_editor_file_loaded(self):
        """Event triggered when editor loaded a file."""
        editor = self.query_exactly_one('#editor', expect_type=Editor)
        self.file = editor.file

    def on_editor_cursor_moved(self):
        """Event triggered when cursor was moved in editor."""
        editor = self.query_exactly_one('#editor', expect_type=Editor)
        self.cursor = editor.cursor_location

    def action_screenshot(self,  filename: str = None, path: str = None):
        """Saves a screenshot of the app in the current folder."""
        folder = Path(path) if path else Path('.')
        if filename:
            file = folder / filename
        else:
            editor = self.query_exactly_one('#editor', expect_type=Editor)
            stem = f'screenshot_{meta.name}'
            if editor.file:
                stem += f'_{editor.file.name}'
            folder = Path('.')
            counter = 1
            while True:
                if counter == 1:
                    file = folder / f'{stem}.svg'
                else:
                    file = folder / f'{stem}_{counter}.svg'
                if not file.exists():
                    break
                counter += 1
        svg = self.export_screenshot(title=meta.name)
        file.write_text(svg, encoding='UTF-8')

    def action_quit(self):
        """Called when the user wants to quit the application."""
        editor = self.query_exactly_one('#editor', expect_type=Editor)
        if not editor.modified:
            self.exit()

        def follow_up(button: str):
            match button:
                case 'save':
                    editor.action_save()
                    self.exit()
                case 'quit':
                    self.exit()
                case 'cancel':
                    pass

        self.push_screen(dialogs.UnsavedFile(), follow_up)
