from typing import Sequence

import polars as pl

from _typeshed import Incomplete

from .describe import DescribeBoolean as DescribeBoolean
from .describe import DescribeContinuous as DescribeContinuous
from .describe import DescribeDatetime as DescribeDatetime
from .describe import DescribeDiscrete as DescribeDiscrete
from .describe import DescribeItem as DescribeItem
from .describe import DescribeNominal as DescribeNominal
from .describe import DescribeOrdinal as DescribeOrdinal
from .describe import DescribeResult as DescribeResult
from .describe import DescribeString as DescribeString
from .describe import Freq as Freq
from .describe import Quantile as Quantile
from .enumerations import MeasurementType as MeasurementType
from .schema import Measurement as Measurement
from .schema import Schema as Schema

log: Incomplete
DEFAULT_PERCENTILES: tuple[float, ...]

def run_describe(
    *,
    df: pl.DataFrame,
    schema: Schema,
    columns: Sequence[str] | None = None,
    weighted: bool = False,
    weight_col: str | None = None,
    drop_nulls: bool = True,
    top_k: int = 10,
    percentiles: Sequence[float] = ...,
) -> DescribeResult: ...
