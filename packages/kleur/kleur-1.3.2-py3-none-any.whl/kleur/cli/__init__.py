from .css import CssArgsParser
from .theme import ThemeArgsParser
from .utils import run_command


def main() -> None:
    run_command(ThemeArgsParser, CssArgsParser)
