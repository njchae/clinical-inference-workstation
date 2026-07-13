"""Build parameter matrices for a DOE sweep.

A *factor* is a named parameter (e.g. ``temperature``) with a list of levels to
evaluate. A *cell* is one concrete combination of levels — a single point in the
parameter space.
"""

from __future__ import annotations

import itertools


def build_full_factorial(factors: dict[str, list]) -> list[dict]:
    """Return every combination of factor levels (the full Cartesian product).

    With no factors this returns a single empty cell ``[{}]`` — the natural
    identity for a product, and a convenient "evaluate once with defaults" case.
    Key order is preserved so downstream artifacts have stable columns.
    """
    names = list(factors)
    level_lists = [factors[name] for name in names]
    return [dict(zip(names, combination)) for combination in itertools.product(*level_lists)]


def build_fractional_factorial(factors: dict[str, list], fraction: int) -> list[dict]:
    """Return a deterministic subset of the full factorial (every ``fraction``-th cell).

    This is a simple, reproducible way to cut the cost of a large grid — not a
    formal resolution-III/IV design. ``fraction=1`` returns the full grid.
    """
    if fraction < 1:
        raise ValueError("fraction must be a positive integer")
    full = build_full_factorial(factors)
    return full[::fraction]
