from typing import Any

import polars as pl
import svy_io as sio

from _typeshed import Incomplete

from svy.core.labels import Label as Label

__all__ = [
    "sio",
    "to_polars",
    "to_writer_table",
    "labels_from_svyio_meta",
    "build_metadata_from_labels",
    "Label",
]

class Label:
    label: Incomplete
    categories: Incomplete
    def __init__(self, *, label: str | None = None, categories: dict | None = None) -> None: ...

def to_polars(df_like: Any) -> pl.DataFrame:
    """Best-effort conversion to Polars without adding hard deps."""

def to_writer_table(df: pl.DataFrame) -> Any:
    """
    Produce a table type that svy-io's writers accept.
    Prefer Polars; fall back to Arrow; then Pandas.
    """

def labels_from_svyio_meta(meta: dict[str, Any]) -> dict[str, Label]:
    """
    Accepts either:
      A) {"variables": {
             "<var>": {"label": "...", "values": {code: "label", ...}}
         }}
      B) {"vars": [{"name":..., "label":..., "label_set":...}],
          "value_labels": [{"set_name":..., "mapping": {...}}, ...]}
    """

def build_metadata_from_labels(
    df: pl.DataFrame, labels_by_var: dict[str, Label]
) -> dict[str, Any]:
    """
    Produce {"var_labels": {...}, "value_labels": {...}} for svy-io writers.

    - var_labels: {var: "Variable label"}
    - value_labels: {var: {code: "text", ...}}
    """
