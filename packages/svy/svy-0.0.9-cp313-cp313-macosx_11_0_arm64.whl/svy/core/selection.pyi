from typing import Mapping, Sequence

from _typeshed import Incomplete

from svy.core.constants import SVY_HIT as SVY_HIT
from svy.core.constants import SVY_PROB as SVY_PROB
from svy.core.constants import SVY_ROW_INDEX as SVY_ROW_INDEX
from svy.core.constants import SVY_WEIGHT as SVY_WEIGHT
from svy.core.enumerations import PPSMethod as PPSMethod
from svy.core.sample import Sample as Sample
from svy.core.types import DF as DF
from svy.core.types import Category as Category
from svy.core.types import Number as Number
from svy.utils.checks import assert_no_missing as assert_no_missing
from svy.utils.checks import drop_missing as drop_missing
from svy.utils.random_state import RandomState as RandomState
from svy.utils.random_state import resolve_random_state as resolve_random_state
from svy.utils.random_state import seed_from_random_state as seed_from_random_state

log: Incomplete

class Selection:
    def __init__(self, sample: Sample) -> None: ...
    def srs(
        self,
        n: int | Mapping[Category, Number],
        *,
        by: str | Sequence[str] | None = None,
        wr: bool = False,
        shuffle: bool = False,
        rstate: RandomState = None,
        drop_nulls: bool = False,
    ) -> Sample:
        """
        Simple Random Sample (SRS), optionally stratified by (stratum × by).

        `n` semantics (identical to PPS and tolerant to partial keys with zero-fill):
        - scalar `n` -> broadcast to each (stratum×by) group (or scalar if ungrouped)
        - mapping keyed by combined (stratum×by) -> pass-through (missing groups -> 0)
        - mapping keyed by by-only -> broadcast within each stratum (missing by -> 0)
        - mapping keyed by stratum-only -> broadcast across by (missing strata -> 0)
        """
    def pps_sys(
        self,
        n: int,
        *,
        by: str | Sequence[str] | None = None,
        sort_by: str | Sequence[str] | None = None,
        shuffle: bool = False,
        rstate: RandomState = None,
        drop_nulls: bool = False,
    ) -> Sample: ...
    def pps_wr(
        self,
        n: int,
        *,
        by: str | Sequence[str] | None = None,
        shuffle: bool = False,
        rstate: RandomState = None,
        drop_nulls: bool = False,
    ) -> Sample: ...
    def pps_brewer(
        self,
        n: int,
        *,
        by: str | Sequence[str] | None = None,
        shuffle: bool = False,
        rstate: RandomState = None,
        drop_nulls: bool = False,
    ) -> Sample: ...
    def pps_murphy(
        self,
        n: int,
        *,
        by: str | Sequence[str] | None = None,
        shuffle: bool = False,
        rstate: RandomState = None,
        drop_nulls: bool = False,
    ) -> Sample: ...
    def pps_rs(
        self,
        n: int,
        *,
        by: str | Sequence[str] | None = None,
        shuffle: bool = False,
        rstate: RandomState = None,
        drop_nulls: bool = False,
    ) -> Sample: ...
