from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .base_errors import SvyError as SvyError

class _SingletonInfoLike(Protocol):
    """Structural type for singleton records to avoid runtime import cycles."""

    stratum_key: str
    stratum_values: Mapping[str, Any] | None
    psu_key: str
    n_observations: int

@dataclass(eq=False)
class SingletonError(SvyError):
    @classmethod
    def from_singletons(
        cls, singletons: _SingletonSeq, where: str = "singleton_handling"
    ) -> SingletonError: ...
