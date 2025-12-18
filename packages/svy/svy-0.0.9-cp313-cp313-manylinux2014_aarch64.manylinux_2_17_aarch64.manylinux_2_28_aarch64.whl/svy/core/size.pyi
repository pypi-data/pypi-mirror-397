from collections.abc import Generator
from typing import Self

import msgspec

from _typeshed import Incomplete

from svy.core.enumerations import OnePropSizeMethod as OnePropSizeMethod
from svy.core.enumerations import PopParam as PopParam
from svy.core.enumerations import PropVarMode as PropVarMode
from svy.core.enumerations import TwoPropsSizeMethod as TwoPropsSizeMethod
from svy.core.types import DomainScalarMap as DomainScalarMap
from svy.core.types import Number as Number

log: Incomplete

class SampSizeConfigs(msgspec.Struct):
    stratified: bool = ...
    pop_size: Number | DomainScalarMap | None = ...
    deff: Number | DomainScalarMap = ...
    resp_rate: Number | DomainScalarMap = ...
    alloc_unit: Number | DomainScalarMap = ...

class TargetProp(msgspec.Struct, frozen=True, tag="prop"):
    p: Number
    moe: Number
    alpha: Number = ...

class TargetMean(msgspec.Struct, frozen=True, tag="mean"):
    sigma: Number
    moe: Number
    alpha: Number = ...

class TargetTwoProps(msgspec.Struct, frozen=True, tag="two_prop"):
    p1: Number
    p2: Number
    alloc_ratio: Number = ...
    alpha: Number = ...
    power: Number = ...

class TargetTwoMeans(msgspec.Struct, frozen=True, tag="two_prop"):
    mu1: Number
    mu2: Number
    alloc_ratio: Number = ...
    alpha: Number = ...
    power: Number = ...

Target = TargetProp | TargetMean | TargetTwoProps | TargetTwoMeans

class Size(msgspec.Struct, frozen=True, tag="size"):
    stratum: str | None = ...
    n0: Number | tuple[Number, Number] = ...
    n1_fpc: Number | tuple[Number, Number] | None = ...
    n2_deff: Number | tuple[Number, Number] | None = ...
    n: Number | tuple[Number, Number] = ...

class SampSize:
    """
    Compute required sample sizes for survey objectives under simple or stratified designs.

    Parameters
    ----------
    pop_size : Number | DomainScalarMap | None, default None
        Target population size. When provided as a mapping, values are interpreted
        per stratum (keys are stratum labels). If omitted, no finite population
        correction is applied.
    deff : Number | DomainScalarMap, default 1.0
        Design effect. May be a scalar or a per-stratum mapping.
    resp_rate : Number | DomainScalarMap, default 1.0
        Anticipated unit response rate. May be a scalar or a per-stratum mapping.
    alloc_unit : Number | DomainScalarMap, default 1
        Allocation unit (e.g., cluster/PSU size or minimum take). May be a scalar
        or a per-stratum mapping.
    stratified : bool, default False
        If ``True``, interpret inputs as stratified. See notes below for rules.
    n_strata : int | None, optional
        Number of strata when ``stratified=True`` and all other parameters are
        scalar; values will be replicated across strata.

    Notes
    -----
    - **Unstratified**: all of ``pop_size``, ``deff``, ``resp_rate``, and
      ``alloc_unit`` must be scalars.
    - **Stratified (per-stratum mappings provided)**: pass dicts for any of the
      parameters to supply per-stratum values.
    - **Stratified (all scalars)**: set ``n_strata`` to a positive integer; scalar
      values will be replicated across strata.
    """

    PRINT_WIDTH: int | None
    def __init__(
        self,
        pop_size: Number | DomainScalarMap | None = None,
        deff: Number | DomainScalarMap = 1.0,
        resp_rate: Number | DomainScalarMap = 1.0,
        alloc_unit: Number | DomainScalarMap = 1,
        stratified: bool = False,
        n_strata: Number | None = None,
    ) -> None: ...
    def to_polars(
        self,
        order_by: str | None = None,
        ascending: bool = True,
        natural: bool = True,
        overall_first: bool = True,
        group_labels: list[str] | None = None,
        include_stratum: bool | None = None,
    ):
        """
        Normalize sizes to a Polars DataFrame.

        - If `include_stratum` is None, it defaults to `self._configs.stratified`.
        - When `include_stratum` is False, the resulting DF will NOT have a 'stratum' column.
        - Handles scalar, stratified, and comparison (tuple) sizes.
        """
    def to_rich_table(self, title: str | None = None):
        """Return a Rich Table (requires `rich`)."""
    def __rich_console__(self, console, options) -> Generator[Incomplete]:
        """
        Rich-native rendering. Keeps API the same, but wraps the table in an outer Panel
        for consistent branding when users do Console().print(obj).
        """
    @property
    def configs(self) -> SampSizeConfigs: ...
    @property
    def target(self) -> Target | None: ...
    @property
    def size(self) -> Size | None: ...
    @property
    def param(self) -> PopParam | None:
        """Return a defensive copy to avoid external mutation."""
    def estimate_prop(
        self,
        p: Number | DomainScalarMap,
        moe: Number | DomainScalarMap,
        *,
        method: OnePropSizeMethod | DomainScalarMap = ...,
        alpha: Number | DomainScalarMap = 0.05,
    ) -> Self: ...
    def compare_props(
        self,
        p1: Number | DomainScalarMap,
        p2: Number | DomainScalarMap,
        *,
        two_sides: bool = True,
        delta: Number | DomainScalarMap = 0.0,
        alloc_ratio: Number = 1.0,
        method: TwoPropsSizeMethod = ...,
        alpha: Number | DomainScalarMap = 0.05,
        power: Number | DomainScalarMap = 0.8,
        var_mode: PropVarMode = ...,
    ) -> Self: ...
    def estimate_mean(
        self,
        sigma: Number | DomainScalarMap,
        moe: Number | DomainScalarMap,
        *,
        method: OnePropSizeMethod | DomainScalarMap = ...,
        alpha: Number = 0.05,
    ) -> Self: ...
    def compare_means(
        self,
        mu1: Number,
        mu2: Number,
        *,
        method: OnePropSizeMethod | DomainScalarMap = ...,
        alloc_ratio: Number = 1.0,
        alpha: Number = 0.05,
        power: Number = 0.8,
    ) -> Self: ...
