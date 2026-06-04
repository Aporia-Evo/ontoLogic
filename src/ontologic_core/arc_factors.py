"""Generic ARC-style factor extraction for the Ontologic B-lane.

This module turns train pairs into experience vectors. The factors are plain
perception measurements from the input canvas and output-cell coordinates; they
are not task-specific ARC primitives.
"""

from __future__ import annotations

from collections import deque
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
    if ((arr < 0) | (arr > 9)).any():
        raise ValueError("ARC grid colours must be integers in 0..9")
    return arr


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else float(num) / float(den)


def _norm_index(index: int, size: int) -> float:
    return _safe_div(index, size - 1)


def _centered_index(index: int, size: int) -> float:
    if size <= 1:
        return 0.0
    return (2.0 * float(index) / float(size - 1)) - 1.0


def _background_color(grid: np.ndarray) -> int:
    colors, counts = np.unique(grid, return_counts=True)
    max_count = counts.max()
    return int(colors[counts == max_count].min())


def _map_output_to_input(
    r: int, c: int, input_shape: tuple[int, int], output_shape: tuple[int, int]
) -> tuple[int, int]:
    in_h, in_w = input_shape
    out_h, out_w = output_shape
    if input_shape == output_shape:
        return r, c
    mapped_r = int(round(_norm_index(r, out_h) * float(in_h - 1))) if in_h > 1 else 0
    mapped_c = int(round(_norm_index(c, out_w) * float(in_w - 1))) if in_w > 1 else 0
    return int(np.clip(mapped_r, 0, in_h - 1)), int(np.clip(mapped_c, 0, in_w - 1))


def _component_factors(
    grid: np.ndarray, background: int
) -> dict[tuple[int, int], tuple[float, ...]]:
    h, w = grid.shape
    labels = np.full((h, w), -1, dtype=np.int64)
    components: list[dict[str, int]] = []

    for start_r in range(h):
        for start_c in range(w):
            if labels[start_r, start_c] >= 0:
                continue
            color = int(grid[start_r, start_c])
            label = len(components)
            labels[start_r, start_c] = label
            cells = [(start_r, start_c)]
            queue: deque[tuple[int, int]] = deque(cells)
            min_r = max_r = start_r
            min_c = max_c = start_c

            while queue:
                r, c = queue.popleft()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if nr < 0 or nr >= h or nc < 0 or nc >= w:
                        continue
                    if labels[nr, nc] >= 0 or int(grid[nr, nc]) != color:
                        continue
                    labels[nr, nc] = label
                    cells.append((nr, nc))
                    queue.append((nr, nc))
                    min_r = min(min_r, nr)
                    max_r = max(max_r, nr)
                    min_c = min(min_c, nc)
                    max_c = max(max_c, nc)

            components.append(
                {
                    "area": len(cells),
                    "min_r": min_r,
                    "max_r": max_r,
                    "min_c": min_c,
                    "max_c": max_c,
                    "color": color,
                }
            )

    areas = np.asarray([component["area"] for component in components], dtype=np.int64)
    largest_area = int(areas.max())
    smallest_area = int(areas.min())
    out: dict[tuple[int, int], tuple[float, ...]] = {}

    for r in range(h):
        for c in range(w):
            component = components[int(labels[r, c])]
            bbox_h = int(component["max_r"] - component["min_r"] + 1)
            bbox_w = int(component["max_c"] - component["min_c"] + 1)
            rel_r = _safe_div(r - int(component["min_r"]), bbox_h - 1)
            rel_c = _safe_div(c - int(component["min_c"]), bbox_w - 1)
            out[(r, c)] = (
                _safe_div(int(component["area"]), h * w),
                _safe_div(bbox_h, h),
                _safe_div(bbox_w, w),
                rel_r,
                rel_c,
                _safe_div(int(component["color"]), 9.0),
                float(int(component["area"]) == largest_area),
                float(int(component["area"]) == smallest_area),
            )
    return out


def _neighborhood_factors(grid: np.ndarray, r: int, c: int, background: int) -> tuple[float, ...]:
    h, w = grid.shape
    color = int(grid[r, c])
    neighbor_colors: list[int] = []
    cardinal_equalities = []
    for dr, dc in ((-1, 0), (1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < h and 0 <= nc < w:
            neighbor_color = int(grid[nr, nc])
            neighbor_colors.append(neighbor_color)
            cardinal_equalities.append(float(neighbor_color == color))
        else:
            cardinal_equalities.append(0.0)

    same_fraction = _safe_div(
        sum(int(neighbor_color == color) for neighbor_color in neighbor_colors),
        len(neighbor_colors),
    )
    non_background_count = float(
        sum(int(neighbor_color != background) for neighbor_color in neighbor_colors)
    )

    dense_cells = []
    for nr in range(max(0, r - 1), min(h, r + 2)):
        for nc in range(max(0, c - 1), min(w, c + 2)):
            dense_cells.append(int(grid[nr, nc]))
    density = _safe_div(sum(int(cell != background) for cell in dense_cells), len(dense_cells))
    return (same_fraction, non_background_count, *cardinal_equalities, density)


def _mapped_color(grid: np.ndarray, out_r: int, out_c: int, output_shape: tuple[int, int]) -> int:
    mapped_r, mapped_c = _map_output_to_input(out_r, out_c, grid.shape, output_shape)
    return int(grid[mapped_r, mapped_c])


def _symmetry_factors(
    grid: np.ndarray, out_r: int, out_c: int, output_shape: tuple[int, int], sampled_color: int
) -> tuple[float, ...]:
    out_h, out_w = output_shape
    horizontal_color = _mapped_color(grid, out_r, out_w - 1 - out_c, output_shape)
    vertical_color = _mapped_color(grid, out_h - 1 - out_r, out_c, output_shape)
    diagonal_valid = out_c < out_h and out_r < out_w
    diagonal_color = _mapped_color(grid, out_c, out_r, output_shape) if diagonal_valid else 0
    return (
        _safe_div(horizontal_color, 9.0),
        _safe_div(vertical_color, 9.0),
        _safe_div(diagonal_color, 9.0),
        float(sampled_color == horizontal_color),
        float(sampled_color == vertical_color),
        float(diagonal_valid and sampled_color == diagonal_color),
        float(diagonal_valid),
    )


def extract_pair_experience(input_grid, output_grid) -> PairExperience:
    """Extract generic factors from one train pair.

    The output grid supplies only the target colour for each output coordinate.
    All factors are derived from the input grid, the two canvas shapes, and the
    output coordinate being represented.
    """

    input_arr = as_grid(input_grid)
    output_arr = as_grid(output_grid)
    in_h, in_w = input_arr.shape
    out_h, out_w = output_arr.shape
    background = _background_color(input_arr)
    component_lookup = _component_factors(input_arr, background)
    same_shape = input_arr.shape == output_arr.shape
    rows: list[list[float]] = []
    targets: list[int] = []

    shape_factors = (
        _safe_div(in_h, 30.0),
        _safe_div(in_w, 30.0),
        _safe_div(out_h, 30.0),
        _safe_div(out_w, 30.0),
        _safe_div(out_h, in_h),
        _safe_div(out_w, in_w),
        _safe_div(out_h - in_h, 30.0),
        _safe_div(out_w - in_w, 30.0),
    )

    for r in range(out_h):
        for c in range(out_w):
            mapped_r, mapped_c = _map_output_to_input(
                r, c, input_arr.shape, output_arr.shape
            )
            sampled_color = int(input_arr[mapped_r, mapped_c])
            centered_r = _centered_index(r, out_h)
            centered_c = _centered_index(c, out_w)
            color_one_hot = [float(sampled_color == color) for color in range(10)]

            row = [
                _norm_index(r, out_h),
                _norm_index(c, out_w),
                centered_r,
                centered_c,
                float(np.hypot(centered_r, centered_c) / np.sqrt(2.0)),
                float(same_shape),
                _norm_index(mapped_r, in_h),
                _norm_index(mapped_c, in_w),
                _safe_div(sampled_color, 9.0),
                *color_one_hot,
                float(sampled_color == background),
                *_neighborhood_factors(input_arr, mapped_r, mapped_c, background),
                *_symmetry_factors(input_arr, r, c, output_arr.shape, sampled_color),
                *component_lookup[(mapped_r, mapped_c)],
                *shape_factors,
            ]
            rows.append(row)
            targets.append(int(output_arr[r, c]))

    features = np.asarray(rows, dtype=np.float64)
    target_arr = np.asarray(targets, dtype=np.int64)
    if not np.isfinite(features).all():
        raise ValueError("non-finite factor extracted")
    return PairExperience(
        features=features, targets=target_arr, output_shape=tuple(output_arr.shape)
    )


def extract_task_experience(task: dict) -> list[PairExperience]:
    """Extract experience from all train pairs in an ARC-style task."""

    pairs: list[PairExperience] = []
    for pair in task.get("train", []):
        if "input" in pair and "output" in pair:
            pairs.append(extract_pair_experience(pair["input"], pair["output"]))
    if not pairs:
        raise ValueError("task has no train pairs with input and output")
    return pairs
