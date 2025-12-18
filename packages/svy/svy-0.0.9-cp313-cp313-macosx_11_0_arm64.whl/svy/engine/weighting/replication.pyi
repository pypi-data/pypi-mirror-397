import numpy as np

from _typeshed import Incomplete
from numpy.typing import NDArray

from svy.utils.random_state import RandomState as RandomState
from svy.utils.random_state import resolve_random_state as resolve_random_state
from svy.utils.random_state import spawn_child_rngs as spawn_child_rngs

FloatArr = NDArray[np.float64]
IntArr: Incomplete
