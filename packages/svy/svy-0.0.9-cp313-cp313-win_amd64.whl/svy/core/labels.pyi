from typing import Iterable, Mapping, Self

import msgspec

from _typeshed import Incomplete

from svy.core.enumerations import MissingKind as MissingKind
from svy.core.types import Category as Category
from svy.core.types import _MissingType
from svy.errors.label_errors import LabelError as LabelError

log: Incomplete

class Label(msgspec.Struct, frozen=True):
    """Variable label + optional value labels (code -> text).

    Notes
    -----
    Label/value-labels are intended for variables measured as
    NOMINAL, ORDINAL, or BOOLEAN (see MeasurementType).
    """

    label: str
    categories: dict[Category, str] | None | _MissingType = ...
    def clone(self, **overrides) -> Self: ...

class CategoryScheme(msgspec.Struct, frozen=True):
    """
    One value-label scheme for a given (concept, locale), with optional missing semantics.

    JSON Persistence Note
    ---------------------
    JSON object keys must be strings, and sets are not JSON-native. The catalog
    serializes schemes using a custom encoder (pairs for mappings; lists for sets),
    see LabellingCatalog.to_bytes/from_bytes.
    """

    id: str
    concept: str
    mapping: dict[Category, str]
    locale: str | None = ...
    title: str | None = ...
    ordered: bool = ...
    missing: set[Category] | None = ...
    missing_kinds: dict[Category, MissingKind] | None = ...
    def clone(self, **overrides) -> Self: ...

def validate_scheme_missing(s: CategoryScheme, *, strict: bool = True) -> None:
    """
    Ensures:
      - No NaN keys in mapping (brittle as dict keys).
      - missing ⊆ mapping.keys()
      - missing_kinds keys ⊆ mapping.keys()
      - If both provided, missing_kinds.keys() ⊆ missing
    """

def normalize_scheme_missing(s: CategoryScheme) -> CategoryScheme:
    """If only missing_kinds given, derive missing as its keys."""

def missing_codes_by_kind(s: CategoryScheme, kinds: set[MissingKind]) -> set[Category]:
    """Collect codes matching any of the requested kinds."""

def make_scheme(
    *,
    concept: str,
    mapping: Mapping[Category, str],
    locale: str | None = None,
    title: str | None = None,
    ordered: bool = False,
    missing: set[Category] | None = None,
    missing_kinds: dict[Category, MissingKind] | None = None,
    id: str | None = None,
) -> CategoryScheme:
    """
    Factory to create a CategoryScheme with a predictable id (concept:locale).
    Pass an explicit id to override.
    """

class LabellingCatalog:
    """Catalogue of reusable value-label schemes (thread-safe, locale-aware).

    Notes
    -----
    Intended for variables measured as NOMINAL, ORDINAL, or BOOLEAN.
    """
    def __init__(
        self,
        schemes: Iterable[CategoryScheme] = (),
        name: str = "default",
        *,
        locale: str | None = None,
    ) -> None: ...
    @property
    def locale(self) -> str | None: ...
    def set_locale(self, locale: str | None) -> None: ...
    def register(self, scheme: CategoryScheme, *, overwrite: bool = False) -> LabellingCatalog: ...
    def register_many(
        self, *schemes: CategoryScheme, overwrite: bool = False
    ) -> LabellingCatalog: ...
    def add_scheme(
        self,
        *,
        concept: str,
        mapping: Mapping[Category, str],
        locale: str | None = None,
        title: str | None = None,
        ordered: bool = False,
        missing: set[Category] | None = None,
        missing_kinds: dict[Category, MissingKind] | None = None,
        id: str | None = None,
        overwrite: bool = False,
    ) -> LabellingCatalog:
        """High-level convenience: build a scheme from kwargs and register it."""
    def add_schemes(self, *defs: dict, overwrite: bool = False) -> LabellingCatalog:
        """Batch add from dictionaries of kwargs accepted by add_scheme."""
    def get(self, scheme_id: str) -> CategoryScheme: ...
    def remove(self, scheme_id: str) -> LabellingCatalog: ...
    def list(
        self, *, locale: str | None = None, concept: str | None = None, ordered: bool | None = None
    ) -> list[CategoryScheme]: ...
    def search(self, q: str) -> list[CategoryScheme]: ...
    def pick(self, concept: str, *, locale: str | None = None) -> CategoryScheme: ...
    def to_label(
        self, var_label: str, scheme_id: str, *, overrides: Mapping[Category, str] | None = None
    ) -> Label: ...
    def to_label_by_concept(
        self,
        var_label: str,
        concept: str,
        *,
        locale: str | None = None,
        overrides: Mapping[Category, str] | None = None,
    ) -> Label: ...
    def to_bytes(self) -> bytes: ...
    @classmethod
    def from_bytes(
        cls, data: bytes, *, name: str = "loaded", locale: str | None = None
    ) -> LabellingCatalog: ...
    def save(self, path: str) -> None: ...
    @classmethod
    def load(
        cls, path: str, *, name: str = "loaded", locale: str | None = None
    ) -> LabellingCatalog: ...

class SchemeCatalogView:
    def __init__(self, catalog: LabellingCatalog) -> None: ...
    @property
    def locale(self): ...
    def set_locale(self, locale: str | None): ...
    def list(self, **kw): ...
    def search(self, q: str): ...
    def get(self, scheme_id: str): ...
    def pick(self, concept: str, *, locale: str | None = None): ...
    def to_label(self, var_label: str, scheme_id: str, **kw): ...
    def to_label_by_concept(self, var_label: str, concept: str, **kw): ...

def is_missing_value(
    value: Category | None,
    *,
    scheme: CategoryScheme | None,
    kinds: set[MissingKind] | None = None,
    treat_null: bool = True,
    treat_nan: bool = True,
) -> bool:
    """Test missingness with an optional policy by kind."""

def recode_for_analysis(
    seq: Iterable[Category | None],
    *,
    scheme: CategoryScheme | None,
    kinds: set[MissingKind] | None = None,
    treat_null: bool = True,
    treat_nan: bool = True,
) -> list[Category | None]:
    """Return a new list where selected missing codes are turned into None."""

def display_text(
    value: Category | None, *, scheme: CategoryScheme | None, null_text: str = ""
) -> str:
    """Return display label (or empty/null_text for NA)."""

def polars_mask(col, scheme: CategoryScheme | None, kinds: set[MissingKind] | None = None):
    """
    Returns a Polars expression masking values that are missing by policy.
    Safe on non-float columns (guards is_nan via cast).
    Usage:
      df.with_columns(pl.when(polars_mask("q1", s)).then(None).otherwise(pl.col("q1")))
    """

def polars_to_analysis(
    col,
    scheme: CategoryScheme | None,
    kinds: set[MissingKind] | None = None,
    alias: str | None = None,
): ...
def polars_to_display(col, scheme: CategoryScheme | None, alias: str | None = None): ...
