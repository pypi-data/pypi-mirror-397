from collections.abc import Generator
from typing import Any, Literal, Mapping, Sequence

import msgspec
import numpy as np
import polars as pl

from _typeshed import Incomplete

from svy.core.enumerations import EstMethod as EstMethod
from svy.core.enumerations import PopParam as PopParam
from svy.core.enumerations import QuantileMethod as QuantileMethod
from svy.core.types import Category as Category
from svy.core.types import Number as Number
from svy.core.types import RandomState as RandomState

log: Incomplete

class ParamEst(msgspec.Struct, frozen=True):
    y: str
    est: Number
    se: Number
    cv: Number
    lci: Number
    uci: Number
    by: tuple[str, ...] | None = ...
    by_level: tuple[Category, ...] | None = ...
    y_level: Category | None = ...
    x: str | None = ...
    x_level: Category | None = ...
    deff: Number | None = ...
    def to_dict(self) -> dict[str, object]: ...
    @classmethod
    def from_dicts(cls, rows: Sequence[Mapping[str, Any]]) -> list["ParamEst"]:
        """
        Convert a list of dicts to ParamEst objects.

        Strict: only current-field keys are allowed (no legacy/extra keys).
        Required keys: y, est, se, cv, lci, uci.
        by/by_level are normalized to tuples; lengths must match when both provided.
        """

class Estimate:
    PRINT_WIDTH: int | None
    DECIMALS: int | dict[str, int] | None
    param: PopParam
    alpha: float
    estimates: ParamEst | list[ParamEst] | None
    covariance: np.ndarray
    strata: Sequence[Category]
    singletons: Sequence[Category]
    domains: Sequence[Category]
    method: EstMethod
    n_strata: int
    n_psus: int
    degrees_freedom: int
    as_factor: bool
    q_method: QuantileMethod
    def __init__(
        self, param: PopParam, *, alpha: float = 0.05, rstate: RandomState = None
    ) -> None: ...
    @property
    def decimals(self) -> int | dict[str, int] | None: ...
    @decimals.setter
    def decimals(self, value: int | dict[str, int] | None) -> None: ...
    @property
    def print_width(self) -> int | None: ...
    @print_width.setter
    def print_width(self, value: int | None) -> None: ...
    @property
    def layout(self) -> Literal["auto", "horizontal", "vertical"]: ...
    @layout.setter
    def layout(self, value: Literal["auto", "horizontal", "vertical"]) -> None: ...
    def set_decimals(self, every: int | None = None, /, **overrides: int) -> Estimate:
        """
        Control printed decimals.

        Usage:
          set_decimals(2)            # all numeric columns to 2 decimals
          set_decimals(2, cv=1)      # all to 2, but CV to 1
          set_decimals(est=0, se=1)  # only specific overrides

        Keys: est, se, lci, uci, cv, deff  (cv applies to the percentage after ×100)
        """
    def set_print_width(self, width: int | None) -> Estimate: ...
    def set_layout(self, layout: Literal["auto", "horizontal", "vertical"]) -> Estimate: ...
    def style(
        self,
        *,
        decimals: int | dict[str, int] | None = None,
        print_width: int | None = None,
        layout: Literal["auto", "horizontal", "vertical"] | None = None,
    ) -> Estimate:
        """Fluent convenience for presentation settings."""
    def to_dicts(self) -> list[dict[str, object]]: ...
    def to_polars(self) -> pl.DataFrame:
        """Return the printable (tidy) Polars DataFrame."""
    def to_polars_printable(self) -> pl.DataFrame: ...
    def __rich_console__(self, console, options) -> Generator[Incomplete]: ...
