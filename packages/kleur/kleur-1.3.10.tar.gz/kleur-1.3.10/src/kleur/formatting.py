import os
import re
import sys
from functools import cache
from typing import TYPE_CHECKING, Self

from kleur import Color

if TYPE_CHECKING:
    from collections.abc import Callable

    from kleur import RGB

ANSI_ESCAPE = "\x1b"
_ANSI_STYLE_REGEX = re.compile(rf"{ANSI_ESCAPE}\[\d+(;\d+)*m")


def ansi(s: str) -> str:
    return f"{ANSI_ESCAPE}[{s}"


def ansi_style(*values: int) -> str:
    return ansi(f"{';'.join(str(v) for v in values)}m")


LINE_UP = ansi("A")
LINE_CLEAR = ansi("2K")

RESET_STYLE = ansi_style(0)


@cache
def has_colors() -> bool:
    no = "NO_COLOR" in os.environ
    yes = "CLICOLOR_FORCE" in os.environ
    maybe = sys.stdout.isatty()
    return not no and (yes or maybe)


def _apply_ansi_style(s: str, *values: int) -> str:
    if values and has_colors():
        return f"{ansi_style(*values)}{s}{RESET_STYLE}"
    return s


type _StringStyler = Callable[[str], str]


def _wrap_ansi_style(*values: int) -> _StringStyler:
    def wrapper(s: str) -> str:
        return _apply_ansi_style(s, *values)

    return wrapper


def strip_ansi_style(s: str) -> str:
    return _ANSI_STYLE_REGEX.sub("", s)


bold = _wrap_ansi_style(1)
faint = _wrap_ansi_style(2)
italic = _wrap_ansi_style(3)
underlined = _wrap_ansi_style(4)
inverse = _wrap_ansi_style(7)
strikethrough = _wrap_ansi_style(9)

black = _wrap_ansi_style(30)
red = _wrap_ansi_style(31)
green = _wrap_ansi_style(32)
yellow = _wrap_ansi_style(33)
blue = _wrap_ansi_style(34)
magenta = _wrap_ansi_style(35)
cyan = _wrap_ansi_style(36)
gray = _wrap_ansi_style(37)

black_background = _wrap_ansi_style(40)
red_background = _wrap_ansi_style(41)
green_background = _wrap_ansi_style(42)
yellow_background = _wrap_ansi_style(43)
blue_background = _wrap_ansi_style(44)
magenta_background = _wrap_ansi_style(45)
cyan_background = _wrap_ansi_style(46)
gray_background = _wrap_ansi_style(47)

light_gray = _wrap_ansi_style(90)
light_red = _wrap_ansi_style(91)
light_green = _wrap_ansi_style(92)
light_yellow = _wrap_ansi_style(93)
light_blue = _wrap_ansi_style(94)
light_magenta = _wrap_ansi_style(95)
light_cyan = _wrap_ansi_style(96)
white = _wrap_ansi_style(97)

OK = green("✔")
FAIL = red("✘")


def color_8bit(fg: int = None, bg: int = None) -> _StringStyler:
    values = []
    if fg:
        values += [38, 5, fg]
    if bg:
        values += [48, 5, bg]
    return _wrap_ansi_style(*values)


def color_rgb(fg: RGB = None, bg: RGB = None) -> _StringStyler:
    values = []
    if fg:
        values += [38, 2, *fg]
    if bg:
        values += [48, 2, *bg]
    return _wrap_ansi_style(*values)


class Colored[T](str):
    value: T
    bg: Color | None
    fg: Color | None
    __slots__ = "bg", "fg", "value"

    def __new__(cls, value: T, fg: Color = None, bg: Color = None) -> Self:
        fg_rgb, bg_rgb = fg.as_rgb if fg else None, bg.as_rgb if bg else None
        instance = super().__new__(cls, color_rgb(fg_rgb, bg_rgb)(str(value)))
        instance.value, instance.fg, instance.bg = (value, fg, bg)
        return instance

    def with_color(self, color: Color) -> Colored:
        return Colored(self.value, color, self.bg)

    def with_background(self, background: Color) -> Colored:
        return Colored(self.value, self.fg, background)


class Highlighter:
    def __init__(self, color: Color) -> None:
        self._color = color

    def __call__(self, s: str, *, inverted: bool = False, enabled: bool = True) -> str:
        if not enabled:
            return s
        c, k = self._color.contrasting_shade_pair
        return Colored(s, *((c, k) if inverted else (k, c)))


CP = Color.Props


class ColorHighlighter:
    def __init__(self, color: Color) -> None:
        self._color = color

    def __call__(
        self, highlighted: CP = CP.ALL, *, enable_bounds_highlights: bool = False
    ) -> str:
        c, highlighter = self._color, Highlighter(self._color)
        # Colors progressively built up with hue, saturation & lightness
        decomposed = [c.with_props(CP.H), c.with_props(CP.NO_L), c]
        # Go over each color property and highlight it if necessary.
        sh, ss, sl = [
            Highlighter(k)(f" {s} ", enabled=p in highlighted)
            for (s, k, p) in zip(c.prop_strings(), decomposed, iter(CP), strict=True)
        ]
        # Highlight the outer brackets (or don't), to make it more clearly
        # noticeable if a color is highlighted.
        is_hl = bool(highlighted) and enable_bounds_highlights
        hsluv, start, end = [highlighter(s, enabled=is_hl) for s in ("HSLuv", "[", "]")]
        return f"{hsluv} {start} {sh} {ss} {sl} {end}"
