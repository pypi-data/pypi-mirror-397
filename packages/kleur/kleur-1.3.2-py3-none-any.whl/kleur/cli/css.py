from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

from kleur import Color, ColorHighlighter, Highlighter, blend_colors
from kleur.interpol import LinearMapping, mapped

from .utils import ArgsParser, check_integer_in_range, print_lines

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Iterator


def _input_comment(color: Color) -> str:
    return f"{Highlighter(color)(f' #{color.as_hex}; ')} {ColorHighlighter(color)()}"


class LinesGenerator(ABC):
    def __init__(self, args: Namespace) -> None:
        self._label, self._include_input = (args.label, args.include_input_shades)
        ibw, ns = (args.include_black_and_white, args.number_of_shades + 1)
        self._shades = [s / ns for s in range(*((0, ns + 1) if ibw else (1, ns)))]

    @abstractmethod
    def _comment_lines(self) -> Iterator[str]: ...

    @abstractmethod
    def _colors(self) -> Iterator[tuple[Color, Color.Props]]: ...

    def lines(self) -> Iterator[str]:
        yield "/*"
        yield from self._comment_lines()
        yield "*/"

        # This intermediate dict will take care of duplicates as a nice side effect. 🫠
        colors = {f"{c.lightness * 100:03.0f}": (c, hp) for c, hp in self._colors()}
        for shade, (color, hl_ps) in sorted(colors.items()):
            hl, hl_c, is_hl = Highlighter(color), ColorHighlighter(color), bool(hl_ps)
            hex_str = f"{hl(' ')}{hl(f'#{color.as_hex};', inverted=is_hl)}{hl(' ')}"
            css_var = f"{hl(f'--{self._label}-{shade}', enabled=is_hl)}:{hex_str}"
            yield f"{css_var}/* {hl_c(hl_ps, enable_bounds_highlights=is_hl)} */"


class LinesGeneratorOneColor(LinesGenerator):
    def __init__(self, args: Namespace) -> None:
        super().__init__(args)
        self._input = Color.from_hex(args.color1)

    def _comment_lines(self) -> Iterator[str]:
        yield f"Based on: {_input_comment(self._input)}"

    def _colors(self) -> Iterator[tuple[Color, Color.Props]]:
        """Generate shades of a color."""
        for s in self._shades:
            yield self._input.shade(s), Color.Props.NONE
        if self._include_input:
            yield self._input, Color.Props.ALL


class LinesGeneratorTwoColors(LinesGenerator):
    def __init__(self, args: Namespace) -> None:
        super().__init__(args)
        self._dynamic_range = args.dynamic_range / 100
        c1, c2 = Color.from_hex(args.color1), Color.from_hex(args.color2)
        self._dark, self._bright = sorted(c1.align_pair(c2))

    def _comment_lines(self) -> Iterator[str]:
        yield "Based on:"
        yield f" Darkest:   {_input_comment(self._dark)}"
        yield f" Brightest: {_input_comment(self._bright)}"

    def _colors(self) -> Iterator[tuple[Color, Color.Props]]:
        """
        Generate shades based on two colors.

        The dynamic range specifies to what degree the hue
        of the input colors will be used as boundaries:
        - dynamic range 0 (0%):
            The shades will interpolate (or extrapolate) between the input colors
        - dynamic range between 0 and 1 (between 0% and 100%):
            The shades will interpolate (or extrapolate) between
            darker / brighter shades of the input colors
        - dynamic range 1 (100%):
            The shades will interpolate (or extrapolate) between
            the darkest & brightest shades of the input colors
        """

        def dynamic_bound(c: Color, edge: Literal[0, 1]) -> Color:
            return c.shade(mapped(self._dynamic_range, (c.lightness, edge)))

        dark_o, bright_o = self._dark, self._bright
        dark_n, bright_n = (dynamic_bound(dark_o, 0), dynamic_bound(bright_o, 1))
        shade_mapping = LinearMapping(dark_n.lightness, bright_n.lightness)
        blend_ = blend_colors(dark_n, bright_n)

        def blend(lightness: float) -> Color:
            return blend_(shade_mapping.position_of(lightness))

        for s in self._shades:
            yield blend(s), Color.Props.NONE

        if self._include_input:
            for old, new in zip((dark_o, bright_o), (dark_n, bright_n), strict=True):
                if old.as_hex == new.as_hex:
                    yield new, Color.Props.ALL
                else:
                    yield blend(old.lightness), Color.Props.L
                    yield new, Color.Props.NO_L


class CssArgsParser(ArgsParser):
    name = "css"

    def _parse_args(self) -> None:
        self._parser.add_argument("-l", "--label", type=str, default="color")
        self._parser.add_argument("-c", "--color1", type=str, required=True)
        self._parser.add_argument("-k", "--color2", type=str)
        self._parser.add_argument(
            "-s", "--number-of-shades", type=check_integer_in_range(1, 99), default=19
        )
        self._parser.add_argument(
            "-b", "--include-black-and-white", action="store_true", default=False
        )
        self._parser.add_argument(
            "-i", "--include-input-shades", action="store_true", default=False
        )
        self._parser.add_argument(
            "-d", "--dynamic-range", type=check_integer_in_range(0, 100), default=0
        )

    def _run_command(self, args: Namespace) -> None:
        gen_cls = LinesGeneratorTwoColors if args.color2 else LinesGeneratorOneColor
        print_lines(gen_cls(args).lines())
