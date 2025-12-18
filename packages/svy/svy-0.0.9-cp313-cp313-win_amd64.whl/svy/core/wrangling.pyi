from typing import Any, Callable, Literal, Mapping, Sequence

from _typeshed import Incomplete

from svy.core.constants import SVY_HIT as SVY_HIT
from svy.core.constants import SVY_PROB as SVY_PROB
from svy.core.constants import SVY_ROW_INDEX as SVY_ROW_INDEX
from svy.core.constants import SVY_WEIGHT as SVY_WEIGHT
from svy.core.design import Design as Design
from svy.core.enumerations import CaseStyle as CaseStyle
from svy.core.enumerations import LetterCase as LetterCase
from svy.core.enumerations import MeasurementType as MeasurementType
from svy.core.expr import SAFE_FUNCS as SAFE_FUNCS
from svy.core.expr import Expr as Expr
from svy.core.expr import col as col
from svy.core.expr import lit as lit
from svy.core.expr import to_polars_expr as to_polars_expr
from svy.core.labels import Label as Label
from svy.core.sample import Sample as Sample
from svy.core.types import MutateValue as MutateValue
from svy.core.types import WhereArg as WhereArg
from svy.errors import DimensionError as DimensionError
from svy.errors import LabelError as LabelError
from svy.errors import MethodError as MethodError
from svy.errors import SvyError as SvyError

log: Incomplete
INTEGER_DTYPES: Incomplete
FLOAT_DTYPES: Incomplete
ExprLike = Expr | str | Callable[[Mapping[str, Expr]], Expr]

class Wrangling:
    def __init__(self, sample: Sample) -> None: ...
    def clean_names(
        self,
        minimal: bool = False,
        remove: str | None = None,
        case_style: CaseStyle = ...,
        letter_case: LetterCase = ...,
    ) -> Sample:
        """
        Clean column names on the DataFrame, and propagate to labels/design.
        """
    def remove_columns(self, columns: str | Sequence[str], *, force: bool = False) -> Sample: ...
    def keep_columns(self, columns: str | Sequence[str], *, force: bool = False) -> Sample: ...
    def top_code(
        self,
        top_codes: Mapping[str, float],
        *,
        replace: bool = False,
        into: Mapping[str, str] | None = None,
    ) -> Sample: ...
    def bottom_code(
        self,
        bottom_codes: Mapping[str, float],
        *,
        replace: bool = False,
        into: Mapping[str, str] | None = None,
    ) -> Sample: ...
    def bottom_and_top_code(
        self,
        bottom_and_top_codes: Mapping[str, tuple[float, float] | list[float]],
        *,
        replace: bool = False,
        into: Mapping[str, str] | None = None,
    ) -> Sample: ...
    def recode(
        self,
        cols: str | list[str],
        recodes: Mapping[Any, Sequence[Any]],
        *,
        replace: bool = False,
        into: Mapping[str, str] | str | None = None,
    ) -> Sample: ...
    def categorize(
        self,
        col: str,
        bins: list[float],
        labels: list[str] | None = None,
        *,
        right: bool = True,
        replace: bool = False,
        into: str | None = None,
    ) -> Sample: ...
    def rename_columns(self, renames: dict[str, str]) -> Sample:
        """
        Rename data columns, update label keys, and rebuild Design with updated
        column references (wgt/stratum/psu/… and replicate-weight names).
        """
    def apply_labels(
        self,
        cols: str | list[str],
        labels: str | list[str],
        categories: dict | None = None,
        *,
        strict: bool = True,
        overwrite: bool = True,
    ) -> Sample:
        """
        Apply variable labels and optional value labels.

        Parameters
        ----------
        cols : str | list[str]
            Variable name(s) to label.
        labels : str | list[str]
            Human-readable label(s), must match length of `vars`.
        categories : dict | None
            Either:
            - global mapping {category_code: "text"} applied to all vars, or
            - per-var mapping {"var": {category_code: "text"}, ...}
            Only meaningful for NOMINAL / ORDINAL / BOOLEAN variables.
        strict : bool
            If True, raise when any variable is missing from the dataframe.
            If False, skip unknown variables silently.
        overwrite : bool
            If False, and a label already exists for a variable, raise.
            If True, replace existing labels.
        """
    def filter_records(
        self,
        where: WhereArg | None = None,
        *,
        negate: bool = False,
        check_singletons: bool = False,
        on_singletons: Literal["ignore", "warn", "error"] = "ignore",
    ) -> Sample:
        """
        Filter Sample._data in place, keeping design/labels/etc. unchanged.

        where:
          - svy Expr (e.g., col("age") >= 18)
          - list/tuple of svy Expr (ANDed)
          - dict[str, scalar | Sequence[scalar]]  -> equality / membership, ANDed
          - None -> no-op
        """
    def mutate(self, specs: Mapping[str, MutateValue], *, inplace: bool = False) -> Sample:
        """
        Like dplyr::mutate / pl.DataFrame.with_columns, but supports:
        - referring to columns created earlier in the same call (batched by deps)
        - literal outputs provided as pl.Series / numpy arrays / python sequences

        Each value in `specs` can be:
        * svy Expr (from svy.core.expr), polars.Expr, or a callable env -> one of those
        * pl.Series of length == n_rows
        * numpy.ndarray / list / tuple of length == n_rows
        """
