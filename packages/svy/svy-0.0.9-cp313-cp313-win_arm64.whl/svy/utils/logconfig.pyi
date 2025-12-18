import logging

from contextlib import contextmanager
from typing import Literal

from .pretty import should_use_rich as should_use_rich

def install_pretty_logging(
    level: int = ...,
    use_rich: bool | str = "auto",
    *,
    replace_handlers: bool = False,
    logger_name: str | None = None,
) -> logging.Handler:
    """
    Configure logging nicely and return the active handler.

    - If replace_handlers=True, existing handlers on the target logger are removed.
    - If handlers already exist and replace_handlers=False, they are kept and the first existing
      handler is returned (no new handler is added).
    """

def enable_logging(
    level: int = ...,
    *,
    use_rich: bool | Literal["auto"] = "auto",
    replace_handlers: bool = False,
    logger_name: str | None = None,
) -> logging.Handler:
    """
    Convenience entry point for apps/notebooks.
    Returns the handler that is active after the call.
    """

def enable_debug(
    *,
    use_rich: bool | Literal["auto"] = "auto",
    replace_handlers: bool = False,
    logger_name: str | None = None,
) -> logging.Handler:
    """Shorthand: DEBUG level."""

@contextmanager
def temporary_log_level(level: int, *, logger_name: str | None = None):
    """
    Context manager to temporarily change the log level.
    """
