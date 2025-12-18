from typing import Any, Sequence

import msgspec
import polars as pl

from _typeshed import Incomplete

from .enumerations import MeasurementType as MeasurementType

log: Incomplete
Categories = Sequence[Any]

class Measurement(msgspec.Struct, frozen=True):
    """
    Immutable definition for a single column.
    - mtype: MeasurementType (what computations to run)
    - categories: only for NOMINAL/ORDINAL/BOOLEAN; order matters for ORDINAL
    - unit/notes: optional metadata
    - na_as_level: treat missing as a category when describing (categoricals/strings)
    """

    mtype: MeasurementType
    categories: Categories | None = ...
    unit: str | None = ...
    notes: str | None = ...
    na_as_level: bool = ...

class Schema(msgspec.Struct):
    """
    Lightweight schema registry mapping column name -> Measurement.
    Mutable API, but stored on Sample and updated via methods to keep state coherent.
    """

    measurements: dict[str, Measurement]
    @classmethod
    def infer(cls, df: pl.DataFrame) -> Schema:
        """Infer a minimal schema from Polars dtypes."""
    def get(self, col: str) -> Measurement | None: ...
    def set(self, col: str, m: Measurement) -> None: ...
    def set_type(self, col: str, mtype: MeasurementType, *, keep_meta: bool = True) -> None: ...
    def set_categories(
        self, col: str, categories: Categories, *, ordered: bool | None = None
    ) -> None:
        """
        Update categories for a column and (optionally) set ordering.

        Rules:
        - ordered=True  -> MeasurementType.ORDINAL
        - ordered=False -> MeasurementType.NOMINAL
        - ordered=None  -> keep current mtype if already NOMINAL/ORDINAL/BOOLEAN,
                            otherwise default to NOMINAL
        """
    def set_na_as_level(self, col: str, flag: bool) -> None: ...
    def set_unit(self, col: str, unit: str | None) -> None: ...
    def set_notes(self, col: str, notes: str | None) -> None: ...
    def align_to_dataframe(self, df: pl.DataFrame) -> None:
        """
        Keep only columns present in df; infer types for any new columns;
        leave existing entries as-is (do not auto-downgrade types).
        """
