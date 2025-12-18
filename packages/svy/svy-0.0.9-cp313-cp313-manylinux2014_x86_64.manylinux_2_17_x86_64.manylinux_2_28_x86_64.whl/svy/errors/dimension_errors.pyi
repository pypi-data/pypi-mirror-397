from dataclasses import dataclass
from typing import Any, Iterable

from .base_errors import SvyError as SvyError

@dataclass(eq=False)
class DimensionError(SvyError):
    """
    Raised for shape/schema/value-size problems: missing columns, incompatible
    dimensions, invalid counts (e.g., n < 0), or sampling size > available rows.
    """

    code = ...
    def __post_init__(self) -> None: ...
    @classmethod
    def invalid_n(
        cls,
        *,
        where: str | None,
        got: Any,
        expected: Any = "n >= 0 or None",
        hint: str | None = "Use None to select all rows.",
        docs_url: str | None = None,
    ) -> DimensionError: ...
    @classmethod
    def missing_columns(
        cls,
        *,
        where: str | None,
        param: str,
        missing: Iterable[str],
        available: Iterable[str] | None = None,
        hint: str | None = "Check spelling or inspect df.columns.",
        docs_url: str | None = None,
    ) -> DimensionError: ...
    @classmethod
    def sample_too_large(
        cls,
        *,
        where: str | None,
        n: int,
        available_rows: int,
        param: str = "n",
        hint: str | None = "When sampling without replacement, ensure n ≤ number of rows.",
        docs_url: str | None = None,
    ) -> DimensionError: ...
    @classmethod
    def empty_estimates(
        cls,
        *,
        where: str | None,
        param: str = "estimates",
        hint: str | None = "Run an analysis first or pass non-empty estimates.",
        docs_url: str | None = None,
    ) -> DimensionError: ...
    @classmethod
    def domain_keys_mismatch(
        cls,
        *,
        where: str | None,
        domain: str,
        expected_keys: Iterable[Any],
        got_keys: Iterable[Any],
        hint: str | None = "Align your provided levels/controls with the domain categories.",
        docs_url: str | None = None,
    ) -> DimensionError: ...
    @classmethod
    def group_levels_mismatch(
        cls,
        *,
        where: str | None,
        var: str,
        expected_levels: Iterable[Any],
        got_levels: Iterable[Any],
        hint: str | None = "Ensure estimates only include the two requested levels.",
        docs_url: str | None = None,
    ) -> DimensionError: ...
