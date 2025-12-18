from dataclasses import dataclass
from typing import Any, Iterable

from .base_errors import SvyError as SvyError

@dataclass(eq=False)
class LabelError(SvyError):
    """Errors related to variable/value labels and label schemes.

    Use this subtype for failures in scheme creation, validation, lookup,
    locale resolution, and (de)serialization.
    """

    code = ...
    def __post_init__(self) -> None: ...
    @classmethod
    def unknown_scheme(
        cls,
        *,
        where: str | None,
        param: str,
        got: Any,
        hint: str | None = "Use catalog.list() or catalog.search() to discover available schemes.",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def scheme_exists(
        cls,
        *,
        where: str | None,
        scheme_id: str,
        hint: str | None = "Pass overwrite=True or choose a different id.",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def invalid_missing_codes(
        cls,
        *,
        where: str | None,
        param: str,
        not_in_mapping: Iterable[Any],
        hint: str | None = "Ensure every missing code appears as a key in mapping.",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def inconsistent_missing_kinds(
        cls,
        *,
        where: str | None,
        offending_keys: Iterable[Any],
        hint: str | None = "Add these codes to 'missing' or remove their kind assignment.",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def nan_key_forbidden(
        cls,
        *,
        where: str | None,
        hint: str
        | None = "Use an explicit code (e.g., 9) for missing; do not use NaN as a dict key.",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def invalid_locale(
        cls,
        *,
        where: str | None,
        got: Any,
        hint: str | None = "Use primary subtags or BCP-47 style locales (e.g., 'en', 'en-US').",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def ambiguous_pick(
        cls,
        *,
        where: str | None,
        concept: str,
        candidates: Iterable[str],
        hint: str | None = "Specify a concrete locale or scheme id to disambiguate.",
        docs_url: str | None = None,
    ) -> LabelError: ...
    @classmethod
    def serialization_error(
        cls,
        *,
        where: str | None,
        reason: str,
        hint: str
        | None = "Ensure mapping keys are JSON-serializable and sets are encoded as lists/tuples.",
        docs_url: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> LabelError: ...
    @classmethod
    def invalid_scheme_id(
        cls,
        *,
        where: str | None,
        got: Any,
        expected: str = "normalized id or 'concept:locale'",
        hint: str | None = "Use make_scheme() to derive an id or pass a normalized id.",
        docs_url: str | None = None,
    ) -> LabelError: ...
