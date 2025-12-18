from typing import Literal, overload

from svy.core.types import Array as Array
from svy.core.types import Category as Category
from svy.core.types import DomainScalarMap as DomainScalarMap
from svy.core.types import FloatArray as FloatArray
from svy.core.types import Number as Number

def calculate_power_array(
    two_sides: bool, delta: Array, sigma: Array, samp_size: Array, alpha: float
) -> FloatArray:
    """
    Typed array variant with explicit float64 arrays and a cast on return to
    satisfy mypy/pyright (some numpy overloads are typed as Any).
    """

def calculate_power_number(
    two_sides: bool, delta: Number, sigma: Number, samp_size: Number, alpha: float
) -> float: ...
def calculate_power_map(
    two_sides: bool,
    delta: DomainScalarMap,
    sigma: DomainScalarMap,
    samp_size: DomainScalarMap,
    alpha: float,
) -> dict[Category, float]: ...
@overload
def calculate_power(
    two_sides: bool, delta: Number, sigma: Number, samp_size: Number, alpha: float
) -> float: ...
@overload
def calculate_power(
    two_sides: bool, delta: Array, sigma: Array, samp_size: Array, alpha: float
) -> FloatArray: ...
@overload
def calculate_power(
    two_sides: bool,
    delta: DomainScalarMap,
    sigma: DomainScalarMap,
    samp_size: DomainScalarMap,
    alpha: float,
) -> dict[Category, float]: ...
def power_for_one_proportion_number(
    prop_0: Number,
    prop_1: Number,
    samp_size: Number,
    *,
    arcsin: bool = True,
    testing_type: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float = 0.05,
) -> float: ...
def power_for_one_proportion_array(
    prop_0: Array,
    prop_1: Array,
    samp_size: Array,
    *,
    arcsin: bool = True,
    testing_type: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float | Array = 0.05,
) -> FloatArray: ...
def power_for_one_proportion_map(
    prop_0: DomainScalarMap,
    prop_1: DomainScalarMap,
    samp_size: DomainScalarMap,
    *,
    arcsin: bool = True,
    testing_type: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float = 0.05,
) -> dict[Category, float]: ...
@overload
def power_for_one_proportion(
    prop_0: Number,
    prop_1: Number,
    samp_size: Number,
    *,
    arcsin: bool = ...,
    testing_type: Literal["two-sided", "less", "greater"] = ...,
    alpha: float = ...,
) -> float: ...
@overload
def power_for_one_proportion(
    prop_0: Array,
    prop_1: Array,
    samp_size: Array,
    *,
    arcsin: bool = ...,
    testing_type: Literal["two-sided", "less", "greater"] = ...,
    alpha: float | Array = ...,
) -> FloatArray: ...
@overload
def power_for_one_proportion(
    prop_0: DomainScalarMap,
    prop_1: DomainScalarMap,
    samp_size: DomainScalarMap,
    *,
    arcsin: bool = ...,
    testing_type: Literal["two-sided", "less", "greater"] = ...,
    alpha: float = ...,
) -> dict[Category, float]: ...
def power_for_two_proportions(
    prop_a: DomainScalarMap | Number | Array,
    prop_b: DomainScalarMap | Number | Array,
    samp_size: DomainScalarMap | Number | Array | None = None,
    ratio: DomainScalarMap | Number | Array | None = None,
    samp_size_a: DomainScalarMap | Number | Array | None = None,
    samp_size_b: DomainScalarMap | Number | Array | None = None,
    testing_type: str = "two-sided",
    alpha: Number | Array = 0.05,
) -> DomainScalarMap | Number | Array:
    """
    Power for testing H0: p_a - p_b = 0 (z-approx). Independent samples.
    If samp_size_a/b are provided, they are used. Otherwise samp_size (+ ratio) is split.
    """

@overload
def power_for_one_mean(
    mean_0: Number,
    mean_1: Number,
    sigma: Number,
    samp_size: Number,
    testing_type: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float = 0.05,
) -> float: ...
@overload
def power_for_one_mean(
    mean_0: Array,
    mean_1: Array,
    sigma: Array,
    samp_size: Array,
    testing_type: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float | Array = 0.05,
) -> FloatArray: ...
@overload
def power_for_one_mean(
    mean_0: DomainScalarMap,
    mean_1: DomainScalarMap,
    sigma: DomainScalarMap,
    samp_size: DomainScalarMap,
    testing_type: Literal["two-sided", "less", "greater"] = "two-sided",
    alpha: float = 0.05,
) -> dict[Category, float]: ...
