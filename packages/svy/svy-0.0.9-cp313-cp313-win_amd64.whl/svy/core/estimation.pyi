from typing import Sequence

from _typeshed import Incomplete

from svy.core.enumerations import EstMethod as EstMethod
from svy.core.enumerations import PopParam as PopParam
from svy.core.enumerations import QuantileMethod as QuantileMethod
from svy.core.estimate import Estimate as Estimate
from svy.core.estimate import ParamEst as ParamEst
from svy.core.sample import Sample as Sample
from svy.utils.checks import assert_no_missing as assert_no_missing
from svy.utils.checks import drop_missing as drop_missing
from svy.utils.random_state import RandomState as RandomState

log: Incomplete

class Estimation:
    def __init__(self, sample: Sample) -> None: ...
    def mean(
        self,
        y: str,
        *,
        by: str | Sequence[str] | None = None,
        deff: bool = False,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def rmean(
        self,
        y: str,
        method: EstMethod,
        *,
        by: str | None = None,
        fay_coef: float = 0.0,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def total(
        self,
        y: str,
        *,
        by: str | None = None,
        deff: bool = False,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def rtotal(
        self,
        y: str,
        method: EstMethod,
        *,
        by: str | None = None,
        fay_coef: float = 0.0,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def prop(
        self,
        y: str,
        *,
        by: str | None = None,
        deff: bool = False,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def rprop(
        self,
        y: str,
        method: EstMethod,
        *,
        by: str | None = None,
        fay_coef: float = 0.0,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def ratio(
        self,
        y: str,
        x: str,
        *,
        by: str | None = None,
        deff: bool = False,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
    def rratio(
        self,
        y: str,
        x: str,
        method: EstMethod = ...,
        *,
        by: str | None = None,
        fay_coef: float = 0.0,
        deff: bool = False,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
        rstate: RandomState = None,
    ) -> Estimate: ...
    def median(
        self,
        y: str,
        *,
        by: str | Sequence[str] | None = None,
        deff: bool = False,
        q_method: QuantileMethod = ...,
        as_factor: bool = False,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Estimate: ...
