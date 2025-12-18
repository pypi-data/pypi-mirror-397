from typing import Hashable, Iterable, TypeAlias

import numpy as np
import numpy.typing as npt

__all__ = ["RandomState", "resolve_random_state", "resolve_seed_sequence", "spawn_child_rngs"]

RandomState: TypeAlias

def resolve_random_state(random_state: RandomState) -> np.random.Generator:
    """
    Resolve a flexible 'random_state' into a np.random.Generator.

    - int           -> seeded Generator
    - SeedSequence  -> Generator from that seed sequence
    - Generator     -> returned as-is
    - None          -> fresh unseeded Generator
    """

def resolve_seed_sequence(random_state: RandomState) -> np.random.SeedSequence:
    """
    Resolve to a SeedSequence for reproducible, order-invariant derivations.

    - int          -> SeedSequence(entropy from hashed int)
    - SeedSequence -> returned as-is
    - Generator    -> SeedSequence derived from generator state (no advance)
    - None         -> SeedSequence from OS entropy (non-deterministic)
    """

def spawn_child_rngs(
    rng_or_state: RandomState,
    keys: npt.NDArray | Iterable[Hashable],
    *,
    salt: bytes = b"",
    digest_size: int = 32,
) -> dict[Hashable, np.random.Generator]:
    """
    Create an independent child Generator for each key (e.g., per stratum),
    reproducibly derived from a root seed.

    Reproducibility:
    - Given the same rng_or_state and the same set of keys (with the same values),
      the mapping is identical for the same input order.
      (If you need order-invariance across different input orders, sort keys before calling.)
    """
