from typing import TYPE_CHECKING

from kleur import GREY, AltColors, Color, Colored, Colors, Highlighter, c

from .utils import (
    ArgsParser,
    check_integer_in_range,
    get_class_vars,
    parse_key_value_pair,
    print_lines,
    try_convert,
)

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Iterable, Iterator


def _block(s: str) -> str:
    return s.center(8)


def _highlight_hex(color: Color, *, inverted: bool = False) -> str:
    return Highlighter(color)(_block(color.as_hex), inverted=inverted)


class LinesGenerator:
    def __init__(self, args: Namespace) -> None:
        ns, nv = args.number_of_shades, args.number_of_vibrances
        self._shades = [s / (ns + 1) for s in range(1, ns + 1)]
        self._vibrances = [v / nv for v in range(1, nv + 1)]

        colors: dict[int, tuple[str, Color]] = {}

        if args.merge_with_default_theme or not args.colors:
            # Add colors from default theme.
            theme_cls = AltColors if args.alt_default_theme else Colors
            for name, color in get_class_vars(theme_cls, Color).items():
                colors[round(color.hue * 360)] = name, color

        # Add custom colors from args.
        for name, hue in args.colors:
            h = try_convert(int, hue, default=333) % 360
            colors[h] = name, c(h)

        self._colors = sorted(colors.items())

    def _blocks(self, last_block: str, color: Color) -> Iterable[str]:
        for s in self._shades:
            yield _highlight_hex(color.shade(s))
        yield Colored(last_block, color)

    def lines(self) -> Iterator[str]:
        yield "".join(self._blocks("     grey", GREY))
        for v in self._vibrances:
            yield "".join(_block(f"{s:.2%}") for s in self._shades)
            for h, (name, color) in self._colors:
                k = color.adjust(saturation=v)
                yield "".join(self._blocks(f" {h:3.0f} {name}", k))


class ThemeArgsParser(ArgsParser):
    name = "theme"

    def _parse_args(self) -> None:
        self._parser.add_argument(
            "-c",
            "--colors",
            nargs="+",
            metavar="NAME=HUE (1-360)",
            type=parse_key_value_pair,
            default={},
        )
        self._parser.add_argument(
            "-m", "--merge-with-default-theme", action="store_true", default=False
        )
        self._parser.add_argument(
            "-a", "--alt-default-theme", action="store_true", default=False
        )
        self._parser.add_argument(
            "-s", "--number-of-shades", type=check_integer_in_range(1, 99), default=9
        )
        self._parser.add_argument(
            "-v", "--number-of-vibrances", type=check_integer_in_range(1, 99), default=2
        )

    def _run_command(self, args: Namespace) -> None:
        print_lines(LinesGenerator(args).lines())
