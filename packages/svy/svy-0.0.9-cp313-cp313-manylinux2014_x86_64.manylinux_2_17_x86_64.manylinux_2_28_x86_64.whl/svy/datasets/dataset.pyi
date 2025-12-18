from typing import Sequence

import polars as pl

from _typeshed import Incomplete

log: Incomplete
BASE_URL: Incomplete

def load_dataset(
    name: str,
    *,
    limit: int | None = 100,
    where: dict | list | None = None,
    select: Sequence[str] | None = None,
    order_by: Sequence[str] | None = None,
    descending: bool | Sequence[bool] = False,
    force_local: bool = False,
) -> pl.DataFrame:
    """
    Load an example dataset from svylab by short name (e.g., 'ea_listing') as a Polars DataFrame.

    - If limit is an int (default 100): use preview endpoint (prefers server-side filtering).
    - If limit is None: download parquet, then apply filters locally (lazy) and collect.
    """
