from _typeshed import Incomplete

SVY_PREFIX: str
SVY_PRIV_PREFIX: str
SVY_ROW_INDEX: Incomplete
SVY_HIT: Incomplete
SVY_PROB: Incomplete
SVY_WEIGHT: Incomplete

def rep_col(i: int) -> str: ...
def tmp_col(tag: str) -> str: ...
def ensure_new_col(cols: list[str], name: str) -> str: ...
