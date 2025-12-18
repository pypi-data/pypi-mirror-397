from typing import Any, Iterable, Self, Sequence, TypeVar

import msgspec

from _typeshed import Incomplete

from svy.core.containers import ChiSquare as ChiSquare
from svy.core.containers import FDist as FDist
from svy.core.enumerations import TableType as TableType
from svy.core.estimate import ParamEst as ParamEst
from svy.core.types import Category as Category
from svy.core.types import Number as Number
from svy.errors import MethodError as MethodError

log: Incomplete

class TableStats(msgspec.Struct):
    pearson_unadj: ChiSquare
    pearson_adj: FDist | None
    lr_unadj: ChiSquare
    lr_adj: FDist | None

class CellEst(msgspec.Struct):
    rowvar: str
    colvar: str
    est: Number
    se: Number
    cv: Number
    lci: Number
    uci: Number
    @classmethod
    def from_param(cls, param_est: ParamEst) -> Self: ...
    def to_dict(self) -> dict[str, Category | None]: ...

class _Missing: ...

T = TypeVar("T")

class Table:
    PRINT_WIDTH: int | None
    DECIMALS: int | dict[str, int] | None
    type: TableType
    rowvar: str
    colvar: str | None
    estimates: Sequence[CellEst] | None
    stats: TableStats | None
    alpha: float
    rowvals: Sequence[Category] | None
    colvals: Sequence[Category] | None
    def __init__(
        self,
        *,
        type: TableType,
        rowvar: str,
        colvar: str | None = None,
        estimates: Sequence[CellEst] | None = None,
        stats: TableStats | None = None,
        rowvals: Sequence[Category] | None = None,
        colvals: Sequence[Category] | None = None,
        alpha: float = 0.05,
    ) -> None: ...
    @classmethod
    def one_way(
        cls,
        *,
        rowvar: str,
        estimates: list[CellEst] | None = None,
        stats: TableStats | None = None,
        rowvals: list[Category] | None = None,
        alpha: float = 0.05,
    ) -> Table: ...
    @classmethod
    def two_way(
        cls,
        *,
        rowvar: str,
        colvar: str,
        estimates: list[CellEst] | None = None,
        stats: TableStats | None = None,
        rowvals: list[Category] | None = None,
        colvals: list[Category] | None = None,
        alpha: float = 0.05,
    ) -> Table: ...
    @property
    def decimals(self) -> int | dict[str, int] | None:
        """Get or set the per-object decimals configuration (int or per-column dict)."""
    @decimals.setter
    def decimals(self, value: int | dict[str, int] | None) -> None: ...
    def set_decimals(self, every: int | None = None, /, **overrides: int) -> Self:
        """
        Fluent helper:
          set_decimals(2)            # all numeric columns to 2
          set_decimals(2, cv=3)      # all to 2, cv to 3
          set_decimals(est=0, se=1)  # only specific overrides
        """
    @property
    def print_width(self) -> int | None:
        """Get or set a per-object preferred print width (overrides class/env)."""
    @print_width.setter
    def print_width(self, value: int | None) -> None: ...
    def style(
        self, *, decimals: int | dict[str, int] | None = None, print_width: int | None = None
    ) -> Self:
        """
        Fluent convenience to set presentation options.
        """
    @property
    def is_crosstab(self) -> bool: ...
    def __setattr__(self, name: str, value: object) -> None: ...
    def __delattr__(self, name: str) -> None: ...
    def __rich_console__(self, console: Any, options: Any) -> Iterable[Any]: ...
    def update(
        self,
        *,
        rowvar: str | _Missing = ...,
        colvar: str | None | _MISSING = ...,
        estimates: Sequence[CellEst] | None | _Missing = ...,
        stats: TableStats | None | _Missing = ...,
        rowvals: Sequence[Category] | None | _Missing = ...,
        colvals: Sequence[Category] | None | _MISSING = ...,
        alpha: float | _Missing = ...,
    ) -> Self: ...
    def fill_missing(
        self,
        *,
        rowvar: str | _Missing = ...,
        colvar: str | None | _Missing = ...,
        estimates: Sequence[CellEst] | None | _MISSING = ...,
        stats: TableStats | None | _MISSING = ...,
        rowvals: Sequence[Category] | _MISSING | None = ...,
        colvals: Sequence[Category] | _MISSING | None = ...,
        alpha: float | _Missing = ...,
    ) -> Self: ...
    def add_estimate(self, cell: CellEst) -> Self: ...
    def extend_estimates(self, cells: Sequence[CellEst]) -> Self: ...
    def add_param(self, param_est: ParamEst) -> Self: ...
    def extend_params(self, params: Sequence[ParamEst]) -> Self: ...
    def set_stats(self, stats: TableStats | None) -> Self: ...
    def set_levels(
        self,
        *,
        rowvals: Sequence[Category] | None = None,
        colvals: Sequence[Category] | None = None,
    ) -> Self: ...
    def to_records(self, *, include_meta: bool = True) -> list[dict[str, Category | None]]: ...
    def to_polars(self) -> Any: ...
    def to_dict(self) -> dict[str, object]: ...
    def show(self, *, decimals: int = 5, use_rich: bool = True) -> None: ...
    def crosstab(
        self,
        stats: str | tuple[str, ...] = "est",
        *,
        by: str | None = None,
        precision: int = 3,
        fill_missing: str | float | None = None,
        cellfmt: str | None = "auto",
        sort_rows: bool = True,
        sort_cols: bool = True,
    ): ...

def show_table(tbl: Table, *, dec: int = 5, use_rich: bool = True) -> None:
    """
    Helper to print a table. 'dec' is a quick override; if the object or class
    has decimals configured, those take precedence unless you explicitly pass
    a different 'dec' here.
    """

def render_plain_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str: ...
