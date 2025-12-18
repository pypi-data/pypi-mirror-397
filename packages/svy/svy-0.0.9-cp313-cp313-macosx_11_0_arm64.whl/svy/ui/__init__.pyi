from typing import Iterable, Mapping

from svy.ui.theme import THEME as THEME

def resolve_width(obj: object | None = None, default: int = 88) -> int:
    """Consistent width resolution (instance → class → module var → __main__ → builtins → env → terminal)."""

def pad(text: str, *, indent: int = 2, surround: bool = False) -> str:
    """Left-pad all lines; optionally add a blank line above and below."""

def styles(obj: object | None = None) -> Mapping[str, str]:
    """Resolve styling from object overrides → theme."""

def render_rich_to_str(renderable, *, width: int) -> str:
    """Render any Rich renderable (or object with __rich_console__) to a string."""

def make_panel(children: Iterable, *, title: str, obj: object | None = None):
    """Panel(Group(children...)) with brand border color."""

def make_table(
    *, header_names: Iterable[str], numeric: set[str] | None = None, obj: object | None = None
):
    """Configured Rich Table with brand header style; right-align numeric columns by name."""
