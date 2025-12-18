from typing import Any, Iterable, Mapping

from _typeshed import Incomplete

from svy.ui.theme import THEME as THEME

log: Incomplete

def resolve_width(owner: object | None = None, default: int = 88, **kwargs: Any) -> int:
    """
    Resolve a preferred print width.

    Backward/forward compatible:
      - resolve_width(owner=...)  (new)
      - resolve_width(obj=...)    (legacy)
    """

def pad(text: str, *, indent: int = 2, surround: bool = False) -> str: ...
def styles(
    obj_or_key: object | str | None = None,
    *,
    kind: str | None = None,
    title: str | None = None,
    border: str | None = None,
    header: str | None = None,
) -> Mapping[str, str]:
    """
    Resolve style dictionary.

    Compatibility:
      - styles(obj, kind="estimate")
      - styles("estimate.results", title="...")  # \'title\' means *style*, not text

    Returns keys: \'border\', \'header\', \'title\'
    """

def panel_enabled(feature_key: str | None = None) -> bool:
    """
    Global/feature switch for wrapping content in an outer Panel.
    Env var SVY_PRINT_PANEL=0/false/off disables panels globally.
    (Extend here if you want per-feature toggles.)
    """

def render_rich_to_str(renderable, *, width: int) -> str: ...
def make_panel(children: Iterable, *, title: str, obj: object | None = None, kind: str = "panel"):
    """
    Legacy helper: constructs a Panel with styles(kind=obj/kind).
    """

def make_table(
    *,
    header_names: Iterable[str],
    numeric: set[str] | None = None,
    obj: object | None = None,
    kind: str = "panel",
    variant: str = "rounded",
):
    """
    Central table builder for components that want to use it.
    Note: Many classes (e.g., Estimate/Table) build their own Rich tables directly.
    """

def build_panel(
    feature_key: str, content, *, default_title: str = "Results", default_border: str = "cyan"
):
    """
    Central panel factory. Controls fit/expand/padding/border/title per feature.

    IMPORTANT: We always use `default_title` for the **text** shown in the panel
    header. Style lookups from `styles(...)` only affect the **appearance** (e.g.,
    border color), not the title text itself.
    """
