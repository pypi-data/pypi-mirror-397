import logging

from contextlib import contextmanager
from typing import Any

from _typeshed import Incomplete

log: Incomplete

@contextmanager
def log_step(logger: logging.Logger, msg: str, /, **fields: Any):
    """
    Context manager: logs 'msg start …' and 'msg done ms=…', and on exceptions logs
    'msg failed …' with a traceback. Very low overhead when DEBUG is off.
    """
