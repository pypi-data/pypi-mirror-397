# python
# -*- coding: utf-8 -*-

"""colortty
A lightweight, chainable helper for composing ANSI escape sequences for colored/styled
terminal text.

Features:
- Foreground and background colors (8-color + bright variants, 256-color index, and truecolor/RGB).
- Text attributes: bold, underline, blink/sparking, inverse, invisible.
- Reusable builder: colortty() returns a Statement you can .set(...) and .make([string]).

Quick start:
    from colortty import colortty, ColorTTY, bold, underline, inverse, invisible

    # Style immediately
    colortty("Hello").set(ColorTTY.Color.red()).set(ColorTTY.BackgroundColor.blue()).make()
    # -> "\033[31;44mHello\033[0m"

    # Reuse a style
    st = colortty().set(ColorTTY.Color.green())
    st.make("Go")                         # "\033[32mGo\033[0m"
    st.set(bold()).make("Go!")            # "\033[32;1mGo!\033[0m"

    # 256-color index and truecolor (RGB)
    colortty("Idx").set(ColorTTY.Color.color_256(208)).make()
    colortty("RGB").set(ColorTTY.Color.color(255, 128, 64)).make()

Notes:
- colortty only builds the styled string; printing is up to you.
- Works in terminals that understand ANSI SGR sequences.
"""

from typing import TYPE_CHECKING

try:
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("colortty")
    except PackageNotFoundError:
        __version__ = "0.0.0"
except BaseException:
    __version__ = "0.0.0"

__author__ = "Ruilx"
__email__ = "RuilxAlxa@qq.com"
__license__ = "MIT"
__url__ = "https://github.com/Ruilx/colortty"
__description__ = "A tiny Python helper to build ANSI escape sequences for terminal styling (colors, backgrounds, and text attributes)."

if TYPE_CHECKING:
    from ._colortty import ColorTTY, colortty, color, background_color, bold, underline, sparking, inverse, invisible


def __getattr__(name: str):
    if name in {"ColorTTY", "colortty", "color", "background_color", "bold", "underline", "sparking", "inverse", "invisible"}:
        from ._colortty import (
            ColorTTY,
            colortty,
            color,
            background_color,
            bold,
            underline,
            sparking,
            inverse,
            invisible,
        )
        return {
            "ColorTTY": ColorTTY,
            "colortty": colortty,
            "color": color,
            "background_color": background_color,
            "bold": bold,
            "underline": underline,
            "sparking": sparking,
            "inverse": inverse,
            "invisible": invisible,
        }[name]
    raise AttributeError(f"module 'colortty' has no attribute {name!r}")


def __dir__():
    return sorted(
        list(globals().keys())
        + [
            "ColorTTY",
            "colortty",
            "color",
            "background_color",
            "bold",
            "underline",
            "sparking",
            "inverse",
            "invisible",
        ]
    )


__all__ = [
    "ColorTTY",
    "colortty",
    "color",
    "background_color",
    "bold",
    "underline",
    "sparking",
    "inverse",
    "invisible",
]
