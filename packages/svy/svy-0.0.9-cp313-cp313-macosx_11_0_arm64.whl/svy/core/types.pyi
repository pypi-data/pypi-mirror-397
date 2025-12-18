from typing import Any, Mapping, Protocol, Sequence, TypeAlias, TypeVar

import numpy as np

from _typeshed import Incomplete
from numpy.typing import NDArray

log: Incomplete
DT = TypeVar("DT", bound=np.generic)
Number: TypeAlias = int | float
Category: TypeAlias = str | int | float | bool
DF: TypeAlias
Array: TypeAlias = NDArray
IntArray: TypeAlias
FloatArray: TypeAlias = NDArray[np.float64]
DictStrArray: TypeAlias = dict[str, Array]
DictStrArrayFloat: TypeAlias = dict[str, FloatArray]
DomainScalarMap: TypeAlias = dict[Category, Number]
DomainCatMap: TypeAlias = dict[Category, DomainScalarMap]
ControlsType: TypeAlias = dict[str, DomainScalarMap]
ControlsLike: TypeAlias = Mapping[str, Mapping[Category, Number]]
RandomState: TypeAlias

class _MissingType: ...

class HasExpr(Protocol):
    """Minimal protocol for svy Expr wrappers (must expose a ._e pl.Expr)."""

ExprLike: TypeAlias
ExprCallable: TypeAlias
SeriesLike: TypeAlias
MutateValue: TypeAlias = ExprLike | ExprCallable | SeriesLike
WhereArg: TypeAlias = None | Mapping[str, Any] | Sequence[ExprLike] | ExprLike
ColumnsArg: TypeAlias = str | Sequence[str] | None
OrderByArg: TypeAlias = str | Sequence[str] | None
DescendingArg: TypeAlias = bool | Sequence[bool]
