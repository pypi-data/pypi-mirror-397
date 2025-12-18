from typing import Any, Literal, Self, Sequence

import polars as pl

from _typeshed import Incomplete

from svy.core.categorical import Categorical
from svy.core.constants import SVY_ROW_INDEX as SVY_ROW_INDEX
from svy.core.describe import DescribeResult as DescribeResult
from svy.core.describe_runtime import run_describe as run_describe
from svy.core.design import Design as Design
from svy.core.design import RepWeights as RepWeights
from svy.core.enumerations import MeasurementType as MeasurementType
from svy.core.estimation import Estimation
from svy.core.expr import to_polars_expr as to_polars_expr
from svy.core.labels import Label as Label
from svy.core.schema import Schema as Schema
from svy.core.selection import Selection
from svy.core.singleton import Singleton
from svy.core.types import DF as DF
from svy.core.types import Category as Category
from svy.core.types import ColumnsArg as ColumnsArg
from svy.core.types import DescendingArg as DescendingArg
from svy.core.types import DomainScalarMap as DomainScalarMap
from svy.core.types import Number as Number
from svy.core.types import OrderByArg as OrderByArg
from svy.core.types import WhereArg as WhereArg
from svy.core.types import _MissingType
from svy.core.warnings import Severity as Severity
from svy.core.warnings import SvyWarning as SvyWarning
from svy.core.warnings import WarnCode as WarnCode
from svy.core.warnings import WarningStore as WarningStore
from svy.core.weighting import Weighting
from svy.core.wrangling import Wrangling
from svy.errors import DimensionError as DimensionError
from svy.errors import MethodError as MethodError
from svy.errors import SvyError as SvyError
from svy.utils.random_state import seed_from_random_state as seed_from_random_state
from svy.utils.trace import log_step as log_step

log: Incomplete
INTEGER_DTYPES: Incomplete
FLOAT_DTYPES: Incomplete

class Sample:
    """A sample class for survey data."""

    PRINT_WIDTH: int | None
    def __init__(self, data: pl.DataFrame, design: Design | None = None) -> None: ...
    def __hash__(self) -> int: ...
    def set_print_width(self, width: int | None) -> Sample:
        """
        Set an object-specific print width. Use None to clear.
        Rules:
          - width must be an int > 20 if not None.
          - This override takes precedence over class/terminal/env defaults.
        """
    @classmethod
    def set_default_print_width(cls, width: int | None) -> None:
        """
        Set a class-wide default print width (int > 20) or None to clear.
        """
    @property
    def weighting(self) -> Weighting: ...
    @property
    def wrangling(self) -> Wrangling: ...
    @property
    def sampling(self) -> Selection: ...
    @property
    def singleton(self) -> Singleton: ...
    @property
    def estimation(self) -> Estimation: ...
    @property
    def categorical(self) -> Categorical: ...
    @property
    def data(self) -> DF:
        """Return a defensive copy to prevent external mutation."""
    @property
    def design(self) -> Design:
        """Return a defensive copy to avoid external mutation of internal design."""
    @property
    def rep_wgts(self) -> RepWeights | None:
        """Return a defensive copy to avoid external mutation of internal rep weights."""
    @property
    def fpc(self) -> dict[Category, Number] | Number: ...
    @property
    def labels(self) -> dict[str, Label]: ...
    @property
    def n_records(self) -> int: ...
    @property
    def n_columns(self) -> int: ...
    @property
    def deff_w(self) -> DomainScalarMap | Number: ...
    @property
    def strata(self): ...
    @property
    def psus(self): ...
    @property
    def ssus(self): ...
    @property
    def schema(self) -> Schema: ...
    @property
    def warnings(self) -> WarningStore: ...
    def set_type(self, col: str, mtype: MeasurementType) -> Sample: ...
    def set_categories(
        self, col: str, categories: Sequence, *, ordered: bool | None = None
    ) -> Sample: ...
    def set_na_as_level(self, col: str, flag: bool = True) -> Sample: ...
    def set_data(self, data: pl.DataFrame) -> Self: ...
    def update_data(self, data: pl.DataFrame) -> Self: ...
    def set_design(self, design: Design) -> Self: ...
    def update_design(self, design: Design) -> Self: ...
    def clone(
        self,
        *,
        data: pl.DataFrame | None | _MissingType = ...,
        design: Design | None | _MissingType = ...,
        rep_wgts: RepWeights | None | _MissingType = ...,
        labels: dict[str, Label] | None | _MissingType = ...,
    ) -> Sample: ...
    def show_data(
        self,
        columns: str | Sequence[str] | None = None,
        *,
        how: Literal["head", "tail", "sample"] = "head",
        n: int | None = 5,
        sort_by: str | Sequence[str] | None = None,
        descending: bool | Sequence[bool] = False,
        nulls_last: bool = False,
        rstate: object | None = None,
    ) -> pl.DataFrame: ...
    def show_records(
        self,
        where: WhereArg = None,
        *,
        columns: ColumnsArg = None,
        order_by: OrderByArg = None,
        descending: DescendingArg = False,
        nulls_last: bool = False,
        n: int | None = 5,
        offset: int = 0,
    ) -> pl.DataFrame: ...
    def describe(
        self,
        columns: Sequence[str] | None = None,
        *,
        weighted: bool = False,
        weight_col: str | None = None,
        drop_nulls: bool = True,
        top_k: int = 10,
        percentiles: Sequence[float] = (0.05, 0.25, 0.5, 0.75, 0.95),
    ) -> DescribeResult:
        """
        Compute a typed description of columns based on the current Schema.

        Internal, concatenated design columns (e.g., stratum/psu/ssu with the internal
        suffix) and the synthetic row index are excluded from the description.
        """
    def warn(
        self,
        *,
        code: WarnCode | str,
        title: str,
        detail: str,
        where: str,
        level: Severity = ...,
        param: str | None = None,
        expected: Any = None,
        got: Any = None,
        hint: str | None = None,
        docs_url: str | None = None,
        extra: dict[str, Any] | None = None,
        var: str | None = None,
        rows: Sequence[int] | None = None,
    ) -> SvyWarning: ...
