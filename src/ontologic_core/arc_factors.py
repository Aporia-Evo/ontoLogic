"""Generic ARC-style factor extraction for the Ontologic B-lane.

This module should turn train pairs into experience vectors. It must not contain
solver-specific ARC heuristics or submission logic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PairExperience:
    """Experience extracted from one input/output pair."""

    features: np.ndarray
    targets: np.ndarray
    output_shape: tuple[int, int]


def as_grid(value) -> np.ndarray:
    """Convert a nested-list ARC grid to a checked integer array."""

    arr = np.asarray(value, dtype=np.int64)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D grid, got shape {arr.shape}")
    if arr.size == 0:
        raise ValueError("empty grids are not supported")
    return arr


def extract_pair_experience(input_grid, output_grid) -> PairExperience:
    """Extract generic factors from one train pair.

    TODO(M16): implement coordinate, colour, neighbourhood, symmetry, and simple
    connected-component factors. This is intentionally a mechanism stub, not a
    solver primitive library.
    """

    raise NotImplementedError("M16 factor extraction is not implemented yet")


def extract_task_experience(task: dict) -> list[PairExperience]:
    """Extract experience from all train pairs in an ARC-style task."""

    pairs: list[PairExperience] = []
    for pair in task.get("train", []):
        if "input" in pair and "output" in pair:
            pairs.append(extract_pair_experience(pair["input"], pair["output"]))
    if not pairs:
        raise ValueError("task has no train pairs with input and output")
    return pairs
