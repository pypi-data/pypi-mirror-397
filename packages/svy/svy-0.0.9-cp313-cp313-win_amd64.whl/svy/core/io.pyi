from pathlib import Path
from typing import Any

import polars as pl

from _typeshed import Incomplete

from svy.core.design import Design as Design
from svy.core.labels import Label as Label
from svy.core.sample import Sample as Sample
from svy.core.types import ColumnsArg as ColumnsArg
from svy.errors.io_errors import IoError as IoError
from svy.errors.io_errors import map_os_error as map_os_error

log: Incomplete

def read_spss(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    design: Design | None = None,
    name: str | None = None,
    encoding: str | None = None,
) -> pl.DataFrame: ...
def read_spss_with_labels(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    design: Design | None = None,
    name: str | None = None,
    encoding: str | None = None,
) -> tuple[pl.DataFrame, dict[str, Label], dict[str, Any]]: ...
def write_spss(sample: Sample, path: str | Path, *, encoding: str | None = None) -> None: ...
def read_stata(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    design: Design | None = None,
    name: str | None = None,
    encoding: str | None = None,
) -> pl.DataFrame: ...
def read_stata_with_labels(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    design: Design | None = None,
    name: str | None = None,
    encoding: str | None = None,
) -> tuple[pl.DataFrame, dict[str, Label], dict[str, Any]]: ...
def write_stata(sample: Sample, path: str | Path, *, version: int | None = None) -> None: ...
def read_sas(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    design: Design | None = None,
    name: str | None = None,
    encoding: str | None = None,
) -> pl.DataFrame: ...
def read_sas_with_labels(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    design: Design | None = None,
    name: str | None = None,
    encoding: str | None = None,
) -> tuple[pl.DataFrame, dict[str, Label], dict[str, Any]]: ...
def write_sas(sample: Sample, path: str | Path, *, format: str | None = None) -> None: ...
def create_from_spss(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    name: str | None = None,
    encoding: str | None = None,
) -> Sample: ...
def create_from_stata(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    name: str | None = None,
    encoding: str | None = None,
) -> Sample: ...
def create_from_sas(
    path: str | Path,
    *,
    columns: ColumnsArg = None,
    name: str | None = None,
    encoding: str | None = None,
) -> Sample: ...

create_from_sav = create_from_spss
read_sav = read_spss
write_sav = write_spss
