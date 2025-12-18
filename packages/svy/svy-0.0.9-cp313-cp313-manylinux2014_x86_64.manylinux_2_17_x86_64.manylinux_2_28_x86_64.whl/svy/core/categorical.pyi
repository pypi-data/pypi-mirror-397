from _typeshed import Incomplete

from svy.core.enumerations import TableType as TableType
from svy.core.enumerations import TableUnits as TableUnits
from svy.core.sample import Sample as Sample
from svy.core.table import Table as Table
from svy.core.ttest import TTestOneGroup as TTestOneGroup
from svy.core.ttest import TTestResults as TTestResults
from svy.core.types import Number as Number
from svy.utils.checks import assert_no_missing as assert_no_missing
from svy.utils.checks import drop_missing as drop_missing

log: Incomplete

class Categorical:
    def __init__(self, sample: Sample) -> None: ...
    def tabulate(
        self,
        rowvar: str,
        colvar: str | None = None,
        *,
        units: TableUnits = ...,
        count_total: float | int | None = None,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> Table: ...
    def ttest_one_group(
        self,
        y: str,
        mean_h0: Number,
        *,
        by: str | None = None,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> TTestOneGroup: ...
    def ttest(
        self,
        y: str,
        *,
        mean_h0: Number = 0,
        group: str | None = None,
        y_pair: str | None = None,
        by: str | None = None,
        alpha: float = 0.05,
        drop_nulls: bool = False,
    ) -> TTestResults: ...
