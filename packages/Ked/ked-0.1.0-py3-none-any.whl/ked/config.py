"""Configuration settings of the application"""

from . import meta

from cyclopts     import App
from platformdirs import user_config_path
from ruamel       import yaml

from pathlib import Path
from shutil  import copy2 as copy


settings = {}
cli = App(
    name     = 'config',
    help     = 'Manage the configuration.',
    sort_key = 2,
)


# Use Ruamel's round-trip parser in order to preserve comments the user may
# have added in the configuration file.
parser = yaml.YAML(typ='rt', pure=True)


@cli.command()
def dir():
    """Show the configuration directory."""
    print(location().parent)


@cli.command()
def file():
    """Show the configuration file."""
    print(location())


def location() -> Path:
    """Returns the platform-dependent location of the configuration file."""
    return user_config_path() / meta.name / 'settings.yaml'


def load(file: Path = None):
    """Loads configuration from `file`, or from `location()` if not given."""
    global settings
    if not file:
        file = location()
    settings = parser.load(file)


def save(file: Path = None):
    """Saves configuration to `file`, or to `location()` if not given."""
    if not file:
        file = location()
    parser.dump(settings, file)


def init():
    """Loads configuration or initializes with defaults if missing."""
    file = location()
    if not file.exists():
        here = Path(__file__).parent
        defaults = here/'defaults.yaml'
        file = location()
        file.parent.mkdir(exist_ok=True)
        copy(defaults, file)
    load(file)
