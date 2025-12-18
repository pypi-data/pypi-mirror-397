from typing import IO, Any

from _typeshed import Incomplete

log: Incomplete

def print_error(err: Any, *, stream=None, prefer_rich: bool | str = "auto") -> None:
    """
    Print an error using Rich if available/desired, else plain text.
    - prefer_rich=True: force Rich if importable
    - prefer_rich=False: force plain
    - prefer_rich="auto": TTY + env heuristics
    """

def want_rich_default(stream: IO[str]) -> bool: ...
def should_use_rich(stream: IO[str] | None = None) -> bool: ...
