from collections.abc import Generator
from typing import Self, Sequence, TypeVar

import msgspec

from _typeshed import Incomplete

from svy.core.enumerations import EstMethod as EstMethod
from svy.core.types import _MissingType

log: Incomplete

class RepWeights(msgspec.Struct, frozen=True):
    """Stores information about replicate weights for variance estimation."""

    method: EstMethod | None = ...
    wgts: tuple[str] = msgspec.field(default_factory=tuple)
    n_reps: int = ...
    fay_coef: float = ...
    df: int = ...
    def clone(self, **overrides) -> Self: ...

T = TypeVar("T")

class Design:
    row_index: str | None
    stratum: str | tuple[str, ...] | None
    wgt: str | None
    prob: str | None
    hit: str | None
    mos: str | None
    psu: str | tuple[str, ...] | None
    ssu: str | tuple[str, ...] | None
    pop_size: str | None
    wr: bool
    rep_wgts: RepWeights | None
    PRINT_WIDTH: int | None
    def __init__(
        self,
        row_index: str | None = None,
        stratum: str | Sequence[str] | None = None,
        wgt: str | None = None,
        prob: str | None = None,
        hit: str | None = None,
        mos: str | None = None,
        psu: str | Sequence[str] | None = None,
        ssu: str | Sequence[str] | None = None,
        pop_size: str | None = None,
        wr: bool = False,
        rep_wgts: RepWeights | None = None,
    ) -> None: ...
    def __setattr__(self, name: str, value: object) -> None: ...
    def __delattr__(self, name: str) -> None: ...
    def __rich_console__(self, console, options) -> Generator[Incomplete]: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def update(
        self,
        *,
        row_index: str | None | _MissingType = ...,
        stratum: str | Sequence[str] | None | _MissingType = ...,
        wgt: str | None | _MissingType = ...,
        prob: str | None | _MissingType = ...,
        hit: str | None | _MissingType = ...,
        mos: str | None | _MissingType = ...,
        psu: str | Sequence[str] | None | _MissingType = ...,
        ssu: str | Sequence[str] | None | _MissingType = ...,
        pop_size: str | None | _MissingType = ...,
        wr: bool | _MissingType = ...,
        rep_wgts: RepWeights | _MissingType | None = ...,
    ) -> Self: ...
    def fill_missing(
        self,
        *,
        row_index: str | None | _MissingType = ...,
        stratum: str | Sequence[str] | None | _MissingType = ...,
        wgt: str | None | _MissingType = ...,
        prob: str | None | _MissingType = ...,
        hit: str | None | _MissingType = ...,
        mos: str | None | _MissingType = ...,
        psu: str | Sequence[str] | None | _MissingType = ...,
        ssu: str | Sequence[str] | None | _MissingType = ...,
        pop_size: str | None | _MissingType = ...,
        wr: bool | _MissingType = ...,
        rep_wgts: RepWeights | Sequence[str] | _MissingType | None = ...,
    ) -> Self: ...
    def update_rep_weights(
        self,
        *,
        wgts: Sequence[str] | _MissingType = ...,
        method: EstMethod | None | _MissingType = ...,
        n_reps: int | _MissingType = ...,
        fay_coef: float | _MissingType = ...,
        df: int | _MissingType = ...,
    ) -> Self:
        """
        Return a new Design with selected RepWeights fields updated.
        Only provided args are changed; others are preserved.
        If no arguments are provided, return self (no-op).
        """
    def specified_fields(self, *, ignore_cols: Sequence[str] | None = None) -> list[str]:
        """
        Return a de-duplicated (order-preserving) list of column names referenced
        by the design (stratum/psu/ssu/etc.) plus any replicate weights.
        """
