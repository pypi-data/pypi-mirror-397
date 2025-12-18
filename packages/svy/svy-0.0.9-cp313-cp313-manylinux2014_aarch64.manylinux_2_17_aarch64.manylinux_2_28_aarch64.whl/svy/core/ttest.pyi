from collections.abc import Generator
from typing import Self

import msgspec

from _typeshed import Incomplete
from msgspec import field

from svy.core.estimate import ParamEst as ParamEst
from svy.core.types import Category as Category
from svy.core.types import Number as Number
from svy.errors import DimensionError as DimensionError
from svy.errors import MethodError as MethodError

log: Incomplete

class TtestEst(msgspec.Struct):
    """Estimate for a (y, group) cell in a t-test context."""

    by: str | None
    by_level: Category | None
    group: str | None
    group_level: Category | None
    y: str
    y_level: Category | None
    est: Number
    se: Number
    cv: Number
    lci: Number
    uci: Number
    @classmethod
    def from_param(cls, param_est: ParamEst) -> Self: ...

class ComparisonProb(msgspec.Struct, frozen=True):
    """One-sided and two-sided p-values for a t statistic."""

    less_than: float
    greater_than: float
    not_equal: float

class TTestStats(msgspec.Struct, frozen=True):
    """Core t-test outputs."""

    df: Number
    value: float
    p_value: ComparisonProb

class GroupLevels(msgspec.Struct, frozen=True):
    """Two-group comparison specification."""

    var: str
    levels: tuple[Category, Category]

class TwoVarianceStats(msgspec.Struct, frozen=True):
    """Report both equal-var and unequal-var (Welch) stats, if available."""

    equal_var: TTestStats | None = ...
    unequal_var: TTestStats | None = ...

class TTestOneGroup(msgspec.Struct, tag="one", tag_field="kind", kw_only=True, frozen=True):
    """One-sample t-test: H0: mean(y) == mean_h0."""

    y: str
    mean_h0: Number = ...
    estimates: list[TtestEst] = field(default_factory=list)
    stats: TTestStats | None = ...
    alpha: float = ...
    def __rich_console__(self, console, options) -> Generator[Incomplete]: ...
    def show(self, *, use_rich: bool = True) -> None:
        """Print to stdout (so pytest capsys can capture)."""

class TTestTwoGroups(msgspec.Struct, tag="two", tag_field="kind", kw_only=True, frozen=True):
    """Two-sample t-test comparing two levels of a grouping variable."""

    y: str
    paired: bool = ...
    groups: GroupLevels
    estimates: list[TtestEst] = field(default_factory=list)
    stats: TwoVarianceStats | None = ...
    alpha: float = ...
    def __rich_console__(self, console, options) -> Generator[Incomplete]: ...
    def show(self, *, use_rich: bool = True) -> None:
        """Print to stdout (so pytest capsys can capture)."""

class TTestResults(msgspec.Struct, frozen=True):
    """Printable container for one or more t-tests."""

    items: tuple[TTestOneGroup | TTestTwoGroups, ...] = ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def __getitem__(self, i): ...
    def __rich_console__(self, console, options) -> Generator[Incomplete]: ...

def ttest_to_records(
    tt: TTestOneGroup | TTestTwoGroups, *, include_meta: bool = True
) -> list[dict]: ...
def ttest_to_polars(tt: TTestOneGroup | TTestTwoGroups): ...
def ttest_to_markdown(tt: TTestOneGroup | TTestTwoGroups, *, dec: int = 4) -> str:
    """Simple Markdown table of estimates; stats summarized below."""
