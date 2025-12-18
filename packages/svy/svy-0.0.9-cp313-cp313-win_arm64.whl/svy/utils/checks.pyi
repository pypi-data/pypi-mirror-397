from typing import Sequence, overload

import numpy as np
import polars as pl

from svy.core.types import Category as Category
from svy.core.types import RandomState as RandomState

def as_1d(*, a: np.ndarray, name: str) -> np.ndarray: ...
def as_float64_1d(*, a: np.ndarray, name: str) -> np.ndarray: ...
def check_same_length(*arrays: tuple[np.ndarray, str]) -> None: ...
def check_weights_finite_positive(*, w: np.ndarray) -> None: ...
def validate_xyw(
    *, y: np.ndarray, w: np.ndarray, x: np.ndarray | None = None, require_x: bool = False
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]: ...
def to_stringnumber(*, token: object) -> Category: ...
def drop_missing(
    *,
    df: pl.DataFrame,
    cols: Sequence[str],
    treat_infinite_as_missing: bool = False,
    streaming: bool = False,
) -> pl.DataFrame:
    """
    Drop rows with NULLs in `cols`, plus NaNs (and optionally ±∞) for float columns.
    """

def assert_no_missing(*, df: pl.DataFrame, subset: Sequence[str]) -> None:
    """Raise with a helpful message if any column in subset has NULL/NaN/±∞."""

@overload
def check_random_state() -> np.random.Generator: ...
@overload
def check_random_state(rstate: None = ...) -> np.random.Generator: ...
@overload
def check_random_state(rstate: int) -> np.random.Generator: ...
@overload
def check_random_state(rstate: np.random.RandomState) -> np.random.Generator: ...
@overload
def check_random_state(rstate: np.random.Generator) -> np.random.Generator: ...
