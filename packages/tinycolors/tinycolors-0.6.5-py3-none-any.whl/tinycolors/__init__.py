"""tinycolors package public surface."""

from typing import Any
from importlib import import_module
from importlib.metadata import version, PackageNotFoundError
from .main import (
    COLOR_MAP,
    BG_COLOR_MAP,
    STYLE_MAP,
    COMBINED_STYLES,
    COMBINED_STYLES_WITH_BG,
    COLOR_NAMES,
    STYLE_NAMES,
    COMBINED_STYLES_LITERAL,
    ColorOptions,
    ColorNotFoundError,
    StyleNotFoundError,
    clib,
)
from .tprint import Supported
# Package version: prefer installed package metadata, fallback to local _version
try:
    __version__ = version("tinycolors")
except PackageNotFoundError:
    try:
        # If you have a local _version.py with __version__ defined
        from ._version import __version__  # type: ignore
    except Exception:
        __version__ = "0.6.1"

# Attempt to import and re-export public names from likely submodules.
__all__ = ["__version__"]

_known_submodules = ("main", "tprint")

for _sub in _known_submodules:
    try:
        _mod = import_module(f".{_sub}", __package__)
    except Exception:
        continue
    for _name in dir(_mod):
        if _name.startswith("_"):
            continue
        # Do not overwrite existing globals
        if _name in globals():
            continue
        globals()[_name] = getattr(_mod, _name)
        __all__.append(_name)

# Provide attribute access helpers (PEP 562)
def __getattr__(name: str):
    if name in globals():
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return sorted(__all__)

__author__ = "Razka Rizaldi"

def colorize(text: Supported,
             color: COLOR_NAMES | None = None,
             style: STYLE_NAMES | None = None,
             bg: COLOR_NAMES | None = None) -> str:
    """Easy colorize function with ANSI escape sequences."""
    color = color or "reset"
    style = style or "reset"
    bg = bg or "reset"

    if color not in COLOR_MAP:
        raise ColorNotFoundError(f"Color {color} is not supported.")
    if style not in STYLE_MAP:
        raise StyleNotFoundError(f"Style {style} is not supported.")
    if bg not in BG_COLOR_MAP:
        raise ColorNotFoundError(f"BG color {bg} is not supported.")

    fg_color = COLOR_MAP[color] if color != "reset" else ""
    bg_color = BG_COLOR_MAP[bg] if bg != "reset" else ""
    text_style = STYLE_MAP[style] if style != "reset" else ""
    return bg_color + fg_color + text_style + str(text) + clib.reset

def colortext(text: Supported, as_: COMBINED_STYLES_LITERAL | str) -> str:
    """
    Simplified color function using combined style names.

    This function provides a cleaner, more intuitive API for colorizing text
    by accepting combined style strings like "bold red" or "italic cyan on blue"
    instead of separate color, style, and background parameters.

    Args:
        text (Supported): The text to colorize
        as_ (COMBINED_STYLES_LITERAL | str): Style string. Can be:
            - Singular color: "red", "blue", "bright green"
            - Singular style: "bold", "italic", "underline"
            - Style + color: "bold red", "italic cyan", "underline blue"
            - Style + color + background: "bold red on black", "italic white on blue"

    Returns:
        Colorized text with ANSI codes and automatic reset at the end

    Examples:
        >>> colortext("Error!", as_="bold red")
        '\\033[1m\\033[31mError!\\033[0m'

        >>> colortext("Success", as_="bold green on black")
        '\\033[1m\\033[32m\\033[40mSuccess\\033[0m'

        >>> colortext("Info", as_="italic bright cyan")
        '\\033[3m\\033[96mInfo\\033[0m'

        >>> colortext("Warning", as_="bold yellow on black")
        '\\033[1m\\033[33m\\033[40mWarning\\033[0m'

        >>> colortext("Simple", as_="red")
        '\\033[31mSimple\\033[0m'

        >>> colortext("Styled", as_="bold")
        '\\033[1mStyled\\033[0m'

    Raises:
        StyleNotFoundError: If the style is not found in the supported styles

    Note:
        The function checks combined styles first, then singular colors, then singular styles.
    """
    # Check COMBINED_STYLES_WITH_BG first (has precedence for "X on Y" patterns)
    if as_ in COMBINED_STYLES_WITH_BG:
        ansi_codes = COMBINED_STYLES_WITH_BG[as_]
        return ansi_codes + str(text) + clib.reset

    # Fall back to COMBINED_STYLES
    if as_ in COMBINED_STYLES:
        ansi_codes = COMBINED_STYLES[as_]
        return ansi_codes + str(text) + clib.reset

    # Check for singular colors
    if as_ in COLOR_MAP:
        ansi_codes = COLOR_MAP[as_]
        return ansi_codes + str(text) + clib.reset

    # Check for singular styles
    if as_ in STYLE_MAP:
        ansi_codes = STYLE_MAP[as_]
        return ansi_codes + str(text) + clib.reset

    # If not found in any, raise an error
    raise StyleNotFoundError(
        f"Style '{as_}' is not supported. "
        f"Use formats like 'red', 'bold', 'bold red', or 'italic cyan on blue'."
    )

def cprint(text: Any,
           color: COLOR_NAMES | None = None,
           style: STYLE_NAMES | None = None,
           bg: COLOR_NAMES | None = None,
           as_: COMBINED_STYLES_LITERAL | str | None = None,
           **print_kwargs: Any) -> None:
    """
    Prints colorized text with support for both individual parameters and combined styles.

    This function supports two APIs:
    1. Legacy API: Use separate color, style, and bg parameters
    2. New API: Use the as_ parameter with combined style strings

    Args:
        text: Text to print
        color: Individual color name (legacy API)
        style: Individual style name (legacy API)
        bg: Individual background color (legacy API)
        as_: Combined style string (new API). Takes precedence over color/style/bg.
        **print_kwargs: Additional keyword arguments passed to print()

    Examples:
        # Old way (still works):
        >>> cprint("text", color="red", style="bold")

        # New way (recommended):
        >>> cprint("text", as_="bold red")
        >>> cprint("text", as_="bold red on blue")
        >>> cprint("Error!", as_="bold white on red")
        >>> cprint("Success!", as_="bold green on black")

        # With print kwargs:
        >>> cprint("text", as_="italic cyan", end="")
        >>> cprint("text", as_="bold yellow", sep=", ")

    Note:
        If as_ is provided, it takes precedence over color, style, and bg parameters.
        The as_ parameter provides a cleaner, more intuitive API.
    """
    # If as_ is provided, use the new colortext() function
    if as_ is not None:
        print(colortext(text, as_=as_), **print_kwargs)
    else:
        # Otherwise use the legacy colorize() for backward compatibility
        print(colorize(text, color=color, style=style, bg=bg), **print_kwargs)

def cinput(text: Any,
           as_: COMBINED_STYLES_LITERAL | str | None = None,
           **kwargs: ColorOptions) -> str:
    """
    Input with colorized prompt supporting both legacy and new APIs.

    This function displays a colorized prompt and returns the user's input.
    It supports two APIs for maximum flexibility.

    Args:
        text: Prompt text to display
        as_: Combined style string (new API). Takes precedence over kwargs.
        **kwargs: ColorOptions dict with 'color', 'style', and 'bg' keys (legacy API)

    Returns:
        User input as a string

    Examples:
        # Old way (still works):
        >>> name = cinput("Name: ", color="blue", style="bold")

        # New way (recommended):
        >>> name = cinput("Name: ", as_="bold blue")
        >>> age = cinput("Age: ", as_="italic cyan")
        >>> email = cinput("Email: ", as_="bold green on black")

    Note:
        If as_ is provided, it takes precedence over kwargs.
        The as_ parameter provides a cleaner, more intuitive API.
    """
    # If as_ is provided, use the new colortext() function
    if as_ is not None:
        return input(colortext(text, as_=as_))
    else:
        # Otherwise use the legacy colorize() with kwargs for backward compatibility
        return input(colorize(text, **kwargs)) # type: ignore