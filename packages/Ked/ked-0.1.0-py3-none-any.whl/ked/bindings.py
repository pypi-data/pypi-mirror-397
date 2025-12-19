"""
Defines the key bindings of application and widgets.

The application and editor widgets don't inherit the default key bindings, as
indicated by the `inherit_bindings=False` subclass argument. We define them
explicitly so that we can drop certain default key bindings we don't care
about. And we add an "id" for each of them to allow the user to remap the keys.
As the lists of key bindings are quite long, they are defined here in this
separate module.

Find a list of accepted `key` values in its Textual's `key.py` module. Find the
default key bindings for the `TextArea` widget in its `widgets/_text_area.py`.
Find a list of accepted `action` values in the reference documentation of the
[`TextArea` widget] via the names of the `action_*` methods.

[`TextArea` widget]: https://textual.textualize.io/widgets/text_area
"""

from textual.binding import Binding


application = [
    Binding(
        key         = 'ctrl+q',
        action      = 'quit',
        description = 'Quit',
        tooltip     = 'Quit app and return to command prompt.',
        priority    = True,
        id          = 'quit_app',
    ),
    Binding(
        key         = 'ctrl+p',
        action      = 'command_palette',
        description = 'Commands',
        tooltip     = 'Show the command palette.',
        priority    = True,
        id          = 'command_palette',
    ),
    Binding(
        key         = 'f5',
        action      = 'change_theme',
        description = 'Theme',
        tooltip     = 'Change the application theme.',
        show        = False,
        id          = 'change_theme',
    ),
]


editor = [

    # File operations
    Binding(
        key         = 'ctrl+s',
        action      = 'save',
        description = 'Save',
        tooltip     = 'Save the file to disk.',
        id          = 'save',
    ),
    Binding(
        key         = 'ctrl+t',
        action      = 'trim_whitespace',
        description = 'Trim white-space',
        tooltip     = 'Trim trailing white-space characters.',
        show        = False,
        id          = 'trim_whitespace',
    ),
    Binding(
        key         = 'ctrl+l',
        action      = 'toggle_wrapping',
        description = 'Toggle wrapping',
        tooltip     = 'Toggle soft-wrapping of long lines.',
        show        = False,
        id          = 'toggle_wrapping',
    ),

    # Clipboard interaction
    Binding(
        key         = 'ctrl+x',
        action      = 'cut',
        description = 'Cut',
        tooltip     = 'Cut selected text and copy it to the clipboard.',
        show        = False,
        id          = 'cut',
    ),
    Binding(
        key         = 'ctrl+c',
        action      = 'copy',
        description = 'Copy',
        tooltip     = 'Copy selected text to the clipboard.',
        show        = False,
        id          = 'copy',
    ),
    Binding(
        key         = 'ctrl+v',
        action      = 'paste',
        description = 'Paste',
        tooltip     = 'Paste text from the clipboard.',
        show        = False,
        id          = 'paste',
    ),

    # Edit history
    Binding(
        key         = 'ctrl+z',
        action      = 'undo',
        description = 'Undo',
        tooltip     = 'Undo the latest editing changes.',
        show        = False,
        id          = 'undo',
    ),
    Binding(
        key         = 'ctrl+y',
        action      = 'redo',
        description = 'Redo',
        tooltip     = 'Redo the latest undone editing changes.',
        show        = False,
        id          = 'redo',
    ),

    # Cursor movement
    Binding(
        key         = 'up',
        action      = 'cursor_up',
        description = 'Up',
        tooltip     = 'Move cursor one line up.',
        show        = False,
        id          = 'cursor_up',
    ),
    Binding(
        key         = 'down',
        action      = 'cursor_down',
        description = 'Down',
        tooltip     = 'Move cursor one line down.',
        show        = False,
        id          = 'cursor_down',
    ),
    Binding(
        key         = 'left',
        action      = 'cursor_left',
        description = 'Left',
        tooltip     = 'Move cursor one character to the left.',
        show        = False,
        id          = 'cursor_left',
    ),
    Binding(
        key         = 'right',
        action      = 'cursor_right',
        description = 'Right',
        tooltip     = 'Move cursor one character to the right.',
        show        = False,
        id          = 'cursor_right',
    ),
    Binding(
        key         = 'ctrl+left',
        action      = 'cursor_word_left',
        description = 'Word left',
        tooltip     = 'Move cursor one word to the left.',
        show        = False,
        id          = 'cursor_word_left',
    ),
    Binding(
        key         = 'ctrl+right',
        action      = 'cursor_word_right',
        description = 'Word right',
        tooltip     = 'Move cursor one word to the right.',
        show        = False,
        id          = 'cursor_word_right',
    ),
    Binding(
        key         = 'home',
        action      = 'cursor_line_start',
        description = 'Home',
        tooltip     = 'Move cursor to start of line.',
        show        = False,
        id          = 'cursor_line_start',
    ),
    Binding(
        key         = 'end',
        action      = 'cursor_line_end',
        description = 'End',
        tooltip     = 'Move cursor to end of line.',
        show        = False,
        id          = 'cursor_line_end',
    ),
    Binding(
        key         = 'pageup',
        action      = 'cursor_page_up',
        description = 'Page up',
        tooltip     = 'Move cursor one screen page up.',
        show        = False,
        id          = 'cursor_page_up',
    ),
    Binding(
        key         = 'pagedown',
        action      = 'cursor_page_down',
        description = 'Page down',
        tooltip     = 'Move cursor one screen page down.',
        show        = False,
        id          = 'cursor_page_down',
    ),

    # Text deletion
    Binding(
        key         = 'backspace',
        action      = 'delete_left',
        description = 'Delete left',
        tooltip     = 'Delete character to the left of cursor.',
        show        = False,
        id          = 'delete_left',
    ),
    Binding(
        key         = 'delete',
        action      = 'delete_right',
        description = 'Delete right',
        tooltip     = 'Delete character to the right of cursor.',
        show        = False,
        id          = 'delete_right',
    ),
    # TODO: Fix this.
    # Ctrl+Backspace does not work in any terminal I've tested.
    # See: https://github.com/Textualize/textual/issues/5134
    # The key binding is usually mapped to Ctrl+W, but I would like to use
    # that to toggle word wrapping.
    # Running the Textual key logger with `textual keys`, I see that in the
    # Windows Terminal, just Backspace is registered as character '\x7f`
    # whereas Ctrl+Backspace is character '\x08'. Maybe that's something
    # to pursue. Like by intercepting the key event and triggering the
    # action that way. T.b.d.
    Binding(
        key         = 'ctrl+backspace',
        action      = 'delete_word_left',
        description = 'Delete word left',
        tooltip     = 'Delete left from cursor to start of word.',
        show        = False,
        id          = 'delete_word_left',
    ),
    Binding(
        key         = 'ctrl+delete',
        action      = 'delete_word_right',
        description = 'Delete word right',
        tooltip     = 'Delete right from cursor until next word.',
        show        = False,
        id          = 'delete_word_right',
    ),

    # Selections
    Binding(
        key         = 'shift+left',
        action      = 'cursor_left(True)',
        description = 'Select left',
        tooltip     = 'Select character to the left of cursor.',
        show        = False,
        id          = 'select_left',
    ),
    Binding(
        key         = 'shift+right',
        action      = 'cursor_right(True)',
        description = 'Select right',
        tooltip     = 'Select character to the right of cursor.',
        show        = False,
        id          = 'select_right',
    ),
    Binding(
        key         = 'ctrl+shift+left',
        action      = 'cursor_word_left(True)',
        description = 'Select word left',
        tooltip     = 'Select from cursor to start of word to the left.',
        show        = False,
        id          = 'select_word_left',
    ),
    Binding(
        key         = 'ctrl+shift+right',
        action      = 'cursor_word_right(True)',
        description = 'Select word right',
        tooltip     = 'Select from cursor to end of word to the right.',
        show        = False,
        id          = 'select_word_right',
    ),
    Binding(
        key         = 'shift+home',
        action      = 'cursor_line_start(True)',
        description = 'Select to line start',
        tooltip     = 'Select from cursor until start of line.',
        show        = False,
        id          = 'select_line_start',
    ),
    Binding(
        key         = 'shift+end',
        action      = 'cursor_line_end(True)',
        description = 'Select to line end',
        tooltip     = 'Select from cursor until end of line.',
        show        = False,
        id          = 'select_line_end',
    ),
    Binding(
        key         = 'shift+up',
        action      = 'cursor_up(True)',
        description = 'Select line up',
        tooltip     = 'Select one line up from cursor.',
        show        = False,
        id          = 'select_line_up',
    ),
    Binding(
        key         = 'shift+down',
        action      = 'cursor_down(True)',
        description = 'Select line down',
        tooltip     = 'Select one line down from cursor.',
        show        = False,
        id          = 'select_line_down',
    ),
    Binding(
        key         = 'ctrl+a',
        action      = 'select_all',
        description = 'Select all',
        tooltip     = 'Select all text.',
        show        = False,
        id          = 'select_all',
    ),
]


horizontal_buttons = [
    Binding(
        key    = 'tab, right',
        action = 'app.focus_next',
        show   = False,
    ),
    Binding(
        key    = 'shift+tab, left',
        action = 'app.focus_previous',
        show   = False,
    ),
    Binding(
        key    = 'escape',
        action = 'cancel',
        show   = False,
    ),
]


vertical_buttons = [
    Binding(
        key    = 'tab, down',
        action = 'app.focus_next',
        show   = False,
    ),
    Binding(
        key    = 'shift+tab, up',
        action = 'app.focus_previous',
        show   = False,
    ),
    Binding(
        key    = 'escape',
        action = 'cancel',
        show   = False,
    ),
]
