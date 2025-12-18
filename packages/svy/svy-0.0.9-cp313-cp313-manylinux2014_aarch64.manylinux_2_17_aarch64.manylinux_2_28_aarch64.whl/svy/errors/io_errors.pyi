from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .base_errors import SvyError as SvyError

@dataclass(eq=False)
class IoError(SvyError):
    """Structured I/O errors for reads/writes across SPSS/Stata/SAS."""

    code = ...
    def __post_init__(self) -> None: ...
    @classmethod
    def not_found(cls, *, where: str | None, path: str | Path) -> IoError: ...
    @classmethod
    def not_a_file(cls, *, where: str | None, path: str | Path) -> IoError: ...
    @classmethod
    def permission_denied(cls, *, where: str | None, path: str | Path) -> IoError: ...
    @classmethod
    def unsupported_ext(
        cls, *, where: str | None, path: str | Path, expected_exts: Iterable[str]
    ) -> IoError: ...
    @classmethod
    def parse_failed(
        cls,
        *,
        where: str | None,
        fmt: str,
        path: str | Path,
        engine_msg: str | None = None,
        hint: str
        | None = "Ensure the file is a valid, uncorrupted data file of the expected format.",
    ) -> IoError: ...
    @classmethod
    def engine_contract_violation(cls, *, where: str | None, got: Any) -> IoError: ...
    @classmethod
    def read_failed(
        cls, *, where: str | None, path: str | Path, reason: str | None = None
    ) -> IoError: ...
    @classmethod
    def write_failed(
        cls, *, where: str | None, path: str | Path, reason: str | None = None
    ) -> IoError: ...

def map_os_error(e: BaseException, *, where: str, path: str | Path) -> IoError: ...
