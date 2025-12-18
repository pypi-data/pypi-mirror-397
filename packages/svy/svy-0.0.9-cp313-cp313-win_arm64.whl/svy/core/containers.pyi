import msgspec

from svy.core.types import Number as Number

class ChiSquare(msgspec.Struct, frozen=True):
    df: Number
    value: Number
    p_value: Number

class FDist(msgspec.Struct, frozen=True):
    df_num: Number
    df_den: Number
    value: Number
    p_value: Number

class TDist(msgspec.Struct, frozen=True):
    df: Number
    value: Number
    p_value: Number
