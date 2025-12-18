from dataclasses import dataclass
from typing import Any, Iterable

from .base_errors import SvyError as SvyError

@dataclass(eq=False)
class MethodError(SvyError):
    """
    Raised when a method/option is invalid or not applicable in the current context.
    Examples: bad enum value, unsupported 'how' mode, incompatible estimator, etc.
    """

    code = ...
    def __post_init__(self) -> None: ...
    @classmethod
    def invalid_choice(
        cls,
        *,
        where: str | None,
        param: str,
        got: Any,
        allowed: Iterable[Any],
        hint: str | None = None,
        docs_url: str | None = None,
    ) -> MethodError: ...
    @classmethod
    def not_applicable(
        cls,
        *,
        where: str | None,
        method: str,
        reason: str,
        param: str | None = None,
        hint: str | None = None,
        docs_url: str | None = None,
    ) -> MethodError: ...
    @classmethod
    def mutate_cycle(cls, cycle_list: str, *, where: str | None = None) -> MethodError: ...
    @classmethod
    def invalid_range(
        cls,
        *,
        where: str | None,
        param: str,
        got: Any,
        min_: float | int | None = None,
        max_: float | int | None = None,
        hint: str | None = None,
        docs_url: str | None = None,
    ) -> MethodError: ...
    @classmethod
    def invalid_type(
        cls,
        *,
        where: str | None,
        param: str,
        got: Any,
        expected: str,
        hint: str | None = None,
        docs_url: str | None = None,
    ) -> MethodError: ...
    @classmethod
    def invalid_mapping_keys(
        cls,
        *,
        where: str | None,
        param: str,
        missing: Iterable[Any] = (),
        extra: Iterable[Any] = (),
        hint: str | None = None,
        docs_url: str | None = None,
    ) -> MethodError: ...
