from typing import Mapping, Sequence

import numpy as np

from _typeshed import Incomplete

from svy.core.design import RepWeights as RepWeights
from svy.core.enumerations import EstMethod as EstMethod
from svy.core.sample import Sample as Sample
from svy.core.types import Category as Category
from svy.core.types import ControlsType as ControlsType
from svy.core.types import DomainScalarMap as DomainScalarMap
from svy.core.types import Number as Number
from svy.errors import DimensionError as DimensionError
from svy.errors import MethodError as MethodError
from svy.utils.checks import drop_missing as drop_missing
from svy.utils.random_state import RandomState as RandomState
from svy.utils.random_state import resolve_random_state as resolve_random_state

log: Incomplete
FLOAT_DTYPES: Incomplete

class Weighting:
    def __init__(self, sample: Sample) -> None: ...
    def create_brr_wgts(
        self,
        n_reps: int | None = None,
        *,
        rep_prefix: str | None = None,
        fay_coef: float = 0.0,
        drop_nulls: bool = False,
    ) -> Sample: ...
    def create_jk_wgts(
        self, *, rep_prefix: str | None = None, drop_nulls: bool = False
    ) -> Sample: ...
    def create_bs_wgts(
        self,
        n_reps: int = 500,
        *,
        rep_prefix: str | None = None,
        drop_nulls: bool = False,
        rstate: RandomState = None,
    ) -> Sample: ...
    def adjust_nr(
        self,
        resp_status: str,
        adj_class: str | Sequence[str] | None,
        *,
        resp_mapping: DomainScalarMap | None = None,
        wgt_name: str | None = None,
        replace: bool = False,
        rep_wgts_prefix: str | None = None,
        ignore_reps: bool = False,
        unknown_to_inelig: bool = True,
        update_design_wgts: bool = True,
        keep_resp: bool = True,
    ) -> Sample: ...
    def normalize(
        self,
        controls: DomainScalarMap | Number | None = None,
        *,
        adj_class: str | Sequence[str] | None = None,
        wgt_name: str | None = None,
        replace: bool = False,
        rep_wgts_prefix: str | None = None,
        ignore_reps: bool = False,
        update_design_wgts: bool = True,
    ) -> Sample: ...
    def poststratify(
        self,
        controls: DomainScalarMap | Number | None = None,
        *,
        factors: DomainScalarMap | Number | None = None,
        adj_class: str | Sequence[str] | None = None,
        wgt_name: str | None = None,
        replace: bool = False,
        rep_wgts_prefix: str | None = None,
        ignore_reps: bool = False,
        update_design_wgts: bool = True,
    ) -> Sample: ...
    def controls_margins_template(
        self, *, margins: Mapping[str, str], cat_na: str = "level", na_label: str = "__NA__"
    ) -> dict[str, dict[Category, float]]:
        """
        Build a per-margin template:
            { margin_name : { category_value -> np.nan } }

        This is handy for raking where you specify margins explicitly by column.
        Assumes margins are *categorical-like*. If a margin column is numeric and
        has many unique values, consider binning/categorizing first.
        """
    def rake(
        self,
        *,
        controls: ControlsType | None = None,
        factors: ControlsType | None = None,
        wgt_name: str | None = None,
        replace: bool = False,
        rep_wgts_prefix: str | None = None,
        ignore_reps: bool = False,
        ll_bound: float | None = None,
        up_bound: float | None = None,
        tol: float = 0.0001,
        max_iter: int = 100,
        display_iter: bool = False,
        update_design_wgts: bool = True,
    ) -> Sample: ...
    def control_aux_template(
        self,
        *,
        cat_vars: str | Sequence[str] | None = None,
        cont_vars: str | Sequence[str] | None = None,
        by: str | Sequence[str] | None = None,
        cat_na: str = "error",
        cont_na: str = "error",
        by_na: str = "error",
        na_label: str = "__NA__",
    ) -> dict[str, object] | dict[Category, dict[str, object]]:
        """
        Preview the expected control structure implied by (cat_vars, cont_vars, by)
        using build_aux_matrix(). Returns either:
          - {label -> nan}                            (when by is None), or
          - {by_value -> {label -> nan}}              (when by is provided).
        """
    def build_aux_matrix(
        self,
        *,
        cat_vars: str | Sequence[str] | None = None,
        cont_vars: str | Sequence[str] | None = None,
        by: str | Sequence[str] | None = None,
        cat_na: str = "error",
        cont_na: str = "error",
        by_na: str = "error",
        na_label: str = "__NA__",
    ) -> tuple[np.ndarray, dict[Category, Number] | dict[Category, dict[Category, Number]]]: ...
    def calibrate(
        self,
        *,
        cat_vars: list[str] | None = None,
        cont_vars: list[str] | None = None,
        by: str | Sequence[str] | None = None,
        controls: dict[Category, Number]
        | dict[Category, dict[Category, Number]]
        | list[Number]
        | np.ndarray
        | Number,
        scale: Number | list[Number] | np.ndarray = 1.0,
        bounded: bool = False,
        additive: bool = False,
        wgt_name: str = "calib_wgt",
        replace: bool = False,
        update_design_wgts: bool = True,
    ):
        """
        Calibrate the current design weights to given control totals.
        Supports tuple keys for multi-categorical covariates and tuple keys for multi-column `by`.
        """
    def calibrate_matrix(
        self,
        *,
        aux_vars: np.ndarray,
        control: dict[Category, dict[Category, Number]]
        | dict[Category, Number]
        | Sequence[Number]
        | np.ndarray
        | Number,
        by: str | Sequence[str] | None = None,
        scale: Number | Sequence[Number] | np.ndarray = 1.0,
        wgt_name: str = "calib_wgt",
        replace: bool = False,
        update_design_wgts: bool = True,
        labels: Sequence[Category] | None = None,
        weights_only: bool = False,
    ):
        """
        Calibrate using a prebuilt design matrix `aux_vars` (X).
        Accepts tuple labels for categorical combinations and tuple keys for multi-column `by`.
        """
