from dataclasses import dataclass, replace
from enum import IntFlag, auto
from functools import cached_property, total_ordering
from typing import TYPE_CHECKING, NamedTuple

from hsluv import hex_to_hsluv, hsluv_to_hex, hsluv_to_rgb, rgb_to_hsluv

from .interpol import mapped, mapped_cyclic, trim, trim_cyclic

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_INCREASE_FACTOR = 2**0.5


class HasNormalizeArgs:
    def _normalize_values(self, funcs: dict[str, Callable[[float], float]]) -> None:
        """
        Make sure all color values are in a valid range.

        object.__setattr__() is one of the awkward options (*) we have,
        when we want to set attributes in a frozen dataclass (which will raise a
        FrozenInstanceError when its own __setattr__() or __delattr__() is invoked).

        *) Another option could be to move the attributes to a super class and
        call super().__init__() here.
        """
        for name, func in funcs.items():
            object.__setattr__(self, name, func(getattr(self, name)))


def normalize_rgb_hex(rgb_hex: str) -> str:
    """
    Try to normalize a hex string into a rrggbb hex.

    :param rgb_hex: RGB hex string (may start with '#')
    :return: rrggbb hex

    >>> normalize_rgb_hex("3")
    '333333'
    >>> normalize_rgb_hex("03")
    '030303'
    >>> normalize_rgb_hex("303")
    '330033'
    >>> normalize_rgb_hex("808303")
    '808303'
    """
    rgb_hex, r, g, b = rgb_hex.removeprefix("#").lower(), "", "", ""

    match len(rgb_hex):
        case 1:
            # 3 -> r=33, g=33, b=33
            r = g = b = rgb_hex * 2

        case 2:
            # 03 -> r=03, g=03, b=03
            r = g = b = rgb_hex

        case 3:
            # 303 -> r=33, g=00, b=33
            r1, g1, b1 = iter(rgb_hex)
            r, g, b = r1 * 2, g1 * 2, b1 * 2

        case 6:
            # 808303 -> r=80, g=83, b=03
            r1, r2, g1, g2, b1, b2 = iter(rgb_hex)
            r, g, b = r1 + r2, g1 + g2, b1 + b2

        case _:
            raise ValueError(rgb_hex)

    return f"{r}{g}{b}"


type RGB = tuple[int, int, int]


class _HSLuv(NamedTuple):
    hue: float
    saturation: float
    lightness: float

    @classmethod
    def from_hex(cls, rgb_hex: str) -> _HSLuv:
        return cls(*hex_to_hsluv(f"#{rgb_hex}"))

    @property
    def as_hex(self) -> str:
        return hsluv_to_hex(self)[1:]

    @classmethod
    def from_rgb(cls, rgb: RGB) -> _HSLuv:
        r, g, b = rgb
        return cls(*rgb_to_hsluv((r / 255, g / 255, b / 255)))

    @property
    def as_rgb(self) -> RGB:
        r, g, b = hsluv_to_rgb(self)
        return round(r * 255), round(g * 255), round(b * 255)


@total_ordering
@dataclass(frozen=True)
class Color(HasNormalizeArgs):
    class Props(IntFlag):
        H = auto()
        S = auto()
        L = auto()
        NONE = 0
        NO_L = H | S
        NO_S = H | L
        ALL = H | S | L

    hue: float = 0  # 0 - 1 (full circle angle)
    saturation: float = 1  # 0 - 1 (ratio)
    lightness: float = 0.5  # 0 - 1 (ratio)

    def __post_init__(self) -> None:
        self._normalize_values(
            {"hue": trim_cyclic, "saturation": trim, "lightness": trim}
        )

    def __repr__(self) -> str:
        sh, ss, sl = self.prop_strings()
        return f"HSLuv({sh}, {ss}, {sl})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Color):
            return self.as_rgb == other.as_rgb
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(iter(self))

    def __lt__(self, other: Color) -> bool:
        return self.as_sortable_tuple < other.as_sortable_tuple

    def __iter__(self) -> Iterator[float]:
        yield self.hue
        yield self.saturation
        yield self.lightness

    def with_props(self, props: Props) -> Color:
        """
        Color built up with from a selection of its original hue, saturation, lightness.

        This could be helpful for understanding how colors
        are built up and relate to each other.
        """
        prop_values = zip(iter(self), iter(self.Props), strict=True)
        return Color(*[v for v, p in prop_values if p in props])

    def prop_strings(self) -> Iterator[str]:
        for v, s in zip(self._as_hsluv, ("°", "%", "%"), strict=True):
            yield f"{v:.2f}{s}".rjust(7)

    def adjust(
        self, *, hue: float = None, saturation: float = None, lightness: float = None
    ) -> Color:
        return Color(
            self.hue + (hue or 0),
            self.saturation * (saturation or 1),
            self.lightness * (lightness or 1),
        )

    def align(self, other: Color) -> Color:
        is_unsaturated = round(self.saturation, 2) == 0
        return self.shifted(other.hue) if is_unsaturated else self

    def align_pair(self, other: Color) -> tuple[Color, Color]:
        aligned_self = self.align(other)
        return aligned_self, other.align(aligned_self)

    @cached_property
    def as_sortable_tuple(self) -> tuple[float, float, float]:
        """Will decide the sort order."""
        return self.lightness, self.saturation, self.hue

    @classmethod
    def _from_hsluv(cls, hsluv: _HSLuv) -> Color:
        return cls(hsluv.hue / 360, hsluv.saturation / 100, hsluv.lightness / 100)

    @cached_property
    def _as_hsluv(self) -> _HSLuv:
        return _HSLuv(self.hue * 360, self.saturation * 100, self.lightness * 100)

    @classmethod
    def from_hex(cls, rgb_hex: str) -> Color:
        """
        Create a Color from an RGB hex string.

        :param rgb_hex: RGB hex string (may start with '#')
        :return: Color instance

        >>> c = Color.from_hex("808303")
        >>> c.as_hex, c.as_rgb
        ('808303', (128, 131, 3))
        >>> k = Color.from_hex("0af")
        >>> k.as_hex, k.as_rgb
        ('00aaff', (0, 170, 255))
        """
        return cls._from_hsluv(_HSLuv.from_hex(normalize_rgb_hex(rgb_hex)))

    @cached_property
    def as_hex(self) -> str:
        return self._as_hsluv.as_hex

    @classmethod
    def from_rgb(cls, rgb: RGB) -> Color:
        """
        Create a Color from RGB values.

        :param rgb: RGB instance
        :return: Color instance

        >>> c = Color.from_rgb((128, 131, 3))
        >>> c.as_hex, c.as_rgb
        ('808303', (128, 131, 3))
        >>> k = Color.from_rgb((0, 170, 255))
        >>> k.as_hex, k.as_rgb
        ('00aaff', (0, 170, 255))
        """
        return cls._from_hsluv(_HSLuv.from_rgb(rgb))

    @cached_property
    def as_rgb(self) -> RGB:
        return self._as_hsluv.as_rgb

    def shifted(self, hue: float) -> Color:
        return replace(self, hue=hue)

    def saturated(self, saturation: float) -> Color:
        return replace(self, saturation=saturation)

    def shade(self, lightness: float) -> Color:
        return replace(self, lightness=lightness)

    def shades(self, n_intervals: int) -> Iterator[Color]:
        for step in range(1, n_intervals):
            yield self.shade(step / n_intervals)

    @cached_property
    def very_bright(self) -> Color:
        return self.shade(5 / 6)

    @cached_property
    def bright(self) -> Color:
        return self.shade(4 / 6)

    @cached_property
    def dark(self) -> Color:
        return self.shade(2 / 6)

    @cached_property
    def very_dark(self) -> Color:
        return self.shade(1 / 6)

    def brighter(self, relative_amount: float = _INCREASE_FACTOR) -> Color:
        return self.adjust(lightness=relative_amount)

    @cached_property
    def slightly_brighter(self) -> Color:
        return self.brighter(_INCREASE_FACTOR**0.5)

    @cached_property
    def much_brighter(self) -> Color:
        return self.brighter(_INCREASE_FACTOR**2)

    def darker(self, relative_amount: float = _INCREASE_FACTOR) -> Color:
        return self.brighter(1 / relative_amount)

    @cached_property
    def slightly_darker(self) -> Color:
        return self.darker(_INCREASE_FACTOR**0.5)

    @cached_property
    def much_darker(self) -> Color:
        return self.darker(_INCREASE_FACTOR**2)

    def blend(self, other: Color, amount: float = 0.5) -> Color:
        return Color(
            mapped_cyclic(amount, (self.hue, other.hue), period=1),
            mapped(amount, (self.saturation, other.saturation)),
            mapped(amount, (self.lightness, other.lightness)),
        )

    @cached_property
    def contrasting_shade(self) -> Color:
        """
        Color with a lightness that contrasts with the current color.

        Color with a 50% lower or higher lightness than the current color,
        while maintaining the same hue and saturation (so it can for example
        be used as background color).

        :return: Color representation of the contrasting shade

        >>> hex_strs = ["08f", "0f8", "80f", "8f0", "f08", "f80"]
        >>> for c, k in [Color.from_hex(h).contrasting_shade_pair for h in hex_strs]:
        ...     print(f"{c.as_hex} <-> {k.as_hex}")
        0088ff <-> 001531
        00ff88 <-> 006935
        8800ff <-> ebe4ff
        88ff00 <-> 366b00
        ff0088 <-> 2b0012
        ff8800 <-> 4a2300
        """
        return self.shade((self.lightness + 0.5) % 1)

    @cached_property
    def contrasting_shade_pair(self) -> tuple[Color, Color]:
        """
        Return this color together with its contrasting shade.

        Turns out to be useful quite commonly in practice, especially in situations
        when you'd want to accommodate a color with a background that would deliver the
        best contrast in terms of visibility.
        """
        return self, self.contrasting_shade

    @cached_property
    def contrasting_hue(self) -> Color:
        """
        Color with a hue that contrasts with the current color.

        Color with a 180° different hue than the current color,
        while maintaining the same saturation and perceived lightness.

        :return: Color representation of the contrasting hue

        >>> hex_strs = ["08f", "0f8", "80f", "8f0", "f08", "f80"]
        >>> for c, k in [Color.from_hex(h).contrasting_hue_pair for h in hex_strs]:
        ...     print(f"{c.as_hex} <-> {k.as_hex}")
        0088ff <-> 9c8900
        00ff88 <-> ffd1f5
        8800ff <-> 5c6900
        88ff00 <-> f6d9ff
        ff0088 <-> 009583
        ff8800 <-> 00b8d1
        """
        return self.adjust(hue=0.5)

    @cached_property
    def contrasting_hue_pair(self) -> tuple[Color, Color]:
        """Return this color together with its contrasting hue."""
        return self, self.contrasting_hue


def blend_colors(c: Color, k: Color) -> Callable[[float], Color]:
    def wrapped(amount: float) -> Color:
        return c.blend(k, amount)

    return wrapped
