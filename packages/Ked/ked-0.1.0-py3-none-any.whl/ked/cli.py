"""Command-line interface of the application"""

from .    import meta
from .    import config
from .tui import TUI

from cyclopts import App, Parameter, Group

from typing  import Annotated
from pathlib import Path


prolog = f"""\
{meta.name}: {meta.summary}

Usage: {meta.name} [FILE | COMMAND]
"""

cli = App(
    name             = meta.name,
    version          = meta.version,
    help             = prolog,
    usage            = '',
    help_flags       = '--help',
    group_arguments  = Group('Argument', sort_key=1),
    group_commands   = Group('Commands', sort_key=2),
    group_parameters = Group('Options',  sort_key=3),
)

cli['--help'].group    = 'Options'
cli['--version'].group = 'Options'

cli.command(config.cli)


@cli.default()
def default(
    file: Annotated[Path, Parameter(name=['FILE'])] = None,
    /,              # Make this a positional argument only, no "--file" option.
) -> int:
    """
    The default command that runs if no other command matched.

    :param file:
        The file to edit. (If shadowed by a command, use "edit" explicitly.)
    """
    if file is None:
        cli.help_print()
        return 0
    if not file.exists():
        error(f'File "{file}" does not exist.')
        print('To create a file and then edit it, use the "edit" command.')
        return 1
    return edit(file)


@cli.command(sort_key=1)
def edit(file: Path) -> int:
    """Edit a given file."""
    config.init()
    tui = TUI()
    tui.file = file
    error_message = tui.run()
    if error_message:
        exit_code = tui.return_code if tui.return_code else 255
        error(error_message)
    else:
        exit_code = tui.return_code if tui.return_code else 0
    return exit_code


def error(message: str):
    """Displays an error message."""
    cli.error_console.print(f'[bold red]Error:[/bold red] {message}')


def print(message: str):
    """Displays an error message."""
    cli.console.print(message)
