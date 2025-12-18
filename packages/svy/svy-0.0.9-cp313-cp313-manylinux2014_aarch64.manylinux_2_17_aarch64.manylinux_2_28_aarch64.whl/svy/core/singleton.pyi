from typing import Any

import msgspec
import polars as pl

from svy.core.enumerations import SingletonMethod
from svy.core.sample import Sample
from svy.errors.singleton_errors import SingletonError as SingletonError

__all__ = ["SingletonInfo", "SingletonResult", "SingletonError", "Singleton"]

class SingletonInfo(msgspec.Struct, frozen=True):
    stratum_key: str
    stratum_values: dict[str, Any]
    psu_key: str
    n_observations: int
    row_indices: tuple[int, ...] | None = ...

class SingletonResult(msgspec.Struct, frozen=True):
    method: SingletonMethod
    detected: tuple[SingletonInfo, ...]
    applied: dict[str, str] | tuple[str, ...] | None = ...
    n_singletons_detected: int = ...
    n_strata_before: int = ...
    n_strata_after: int = ...
    n_psus_before: int = ...
    n_psus_after: int = ...

class Singleton:
    """
    Facet for detecting and handling singleton PSUs.

    Access via: sample.singleton
    """
    def __init__(self, sample: Sample) -> None: ...
    def detected(self) -> list[SingletonInfo]:
        """Detect singleton strata from the sample’s current data/design."""
    def show(self) -> pl.DataFrame:
        """Tabular view of detected singletons."""
    def keys(self) -> list[str]:
        """Convenience accessor for singleton stratum keys (concatenated representation)."""
    def raise_error(self) -> None: ...
    def certainty(self) -> Sample: ...
    def skip(self) -> Sample:
        """Remove all rows belonging to singleton strata."""
    def combine(self, mapping: dict[str, str]) -> Sample:
        """Remap singleton stratum keys to target non-singleton strata."""
