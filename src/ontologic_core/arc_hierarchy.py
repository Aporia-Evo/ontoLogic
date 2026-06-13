"""Hierarchical ARC scene factors for Ontologic B-lane diagnostics.

The functions in this module analyse one input canvas at a time. They expose
object-, scene-, and simple relational measurements that can enrich train-pair
experience without constructing outputs or adding task-specific transforms.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SceneStats:
    """Global measurements for one ARC-style input scene."""

    height: int
    width: int
    background_color: int
    color_counts: tuple[int, ...]
    non_background_count: int
    component_count: int
    unique_color_count: int
    foreground_density: float


@dataclass(frozen=True)
class Component:
    """Measurements for one non-background same-colour connected component."""

    component_id: int
    color: int
    area: int
    bbox: tuple[int, int, int, int]
    centroid_r: float
    centroid_c: float
    bbox_height: int
    bbox_width: int
    touches_border: bool
    is_largest: bool
    is_smallest: bool
    normalized_area: float
    normalized_bbox_size: float
    relative_centroid: tuple[float, float]
    simple_hole_count: int


@dataclass(frozen=True)
class SceneAnalysis:
    """Complete deterministic analysis of one input scene."""

    stats: SceneStats
    components: tuple[Component, ...]
    labels: np.ndarray


def _as_checked_grid(grid) -> np.ndarray:
    arr = np.asarray(grid, dtype=np.int64)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D grid, got shape {arr.shape}")
    if arr.size == 0:
        raise ValueError("empty grids are not supported")
    if ((arr < 0) | (arr > 9)).any():
        raise ValueError("ARC grid colours must be integers in 0..9")
    return arr


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else float(num) / float(den)


def _relative_index(index: float, size: int) -> float:
    return _safe_div(index, size - 1)


def _background_color_and_counts(grid: np.ndarray) -> tuple[int, tuple[int, ...]]:
    counts = tuple(int(np.count_nonzero(grid == color)) for color in range(10))
    max_count = max(counts)
    background = min(color for color, count in enumerate(counts) if count == max_count)
    return background, counts


def analyze_scene(grid) -> SceneAnalysis:
    """Return deterministic component and scene measurements for ``grid``.

    Components are non-background same-colour connected components under a
    4-neighbourhood. The background colour is the most frequent colour, with a
    lowest-colour tie break.
    """

    arr = _as_checked_grid(grid)
    height, width = arr.shape
    background, color_counts = _background_color_and_counts(arr)
    labels = np.full((height, width), -1, dtype=np.int64)
    raw_components: list[dict[str, object]] = []

    for start_r in range(height):
        for start_c in range(width):
            if labels[start_r, start_c] >= 0 or int(arr[start_r, start_c]) == background:
                continue

            component_id = len(raw_components)
            color = int(arr[start_r, start_c])
            labels[start_r, start_c] = component_id
            queue: deque[tuple[int, int]] = deque([(start_r, start_c)])
            cells: list[tuple[int, int]] = [(start_r, start_c)]
            min_r = max_r = start_r
            min_c = max_c = start_c

            while queue:
                r, c = queue.popleft()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if nr < 0 or nr >= height or nc < 0 or nc >= width:
                        continue
                    if labels[nr, nc] >= 0 or int(arr[nr, nc]) != color:
                        continue
                    labels[nr, nc] = component_id
                    queue.append((nr, nc))
                    cells.append((nr, nc))
                    min_r = min(min_r, nr)
                    max_r = max(max_r, nr)
                    min_c = min(min_c, nc)
                    max_c = max(max_c, nc)

            raw_components.append(
                {
                    "component_id": component_id,
                    "color": color,
                    "cells": tuple(cells),
                    "bbox": (min_r, min_c, max_r, max_c),
                }
            )

    areas = [len(component["cells"]) for component in raw_components]
    largest_area = max(areas) if areas else 0
    smallest_area = min(areas) if areas else 0
    components: list[Component] = []

    for component in raw_components:
        cells = component["cells"]
        assert isinstance(cells, tuple)
        min_r, min_c, max_r, max_c = component["bbox"]  # type: ignore[misc]
        bbox_height = int(max_r - min_r + 1)
        bbox_width = int(max_c - min_c + 1)
        area = len(cells)
        centroid_r = float(sum(r for r, _ in cells)) / float(area)
        centroid_c = float(sum(c for _, c in cells)) / float(area)
        touches_border = min_r == 0 or min_c == 0 or max_r == height - 1 or max_c == width - 1
        simple_hole_count = _simple_enclosed_background_count(
            arr, background, int(min_r), int(min_c), int(max_r), int(max_c)
        )
        components.append(
            Component(
                component_id=int(component["component_id"]),
                color=int(component["color"]),
                area=area,
                bbox=(int(min_r), int(min_c), int(max_r), int(max_c)),
                centroid_r=centroid_r,
                centroid_c=centroid_c,
                bbox_height=bbox_height,
                bbox_width=bbox_width,
                touches_border=bool(touches_border),
                is_largest=area == largest_area,
                is_smallest=area == smallest_area,
                normalized_area=_safe_div(area, height * width),
                normalized_bbox_size=_safe_div(bbox_height * bbox_width, height * width),
                relative_centroid=(
                    _relative_index(centroid_r, height),
                    _relative_index(centroid_c, width),
                ),
                simple_hole_count=simple_hole_count,
            )
        )

    non_background_count = int(sum(count for color, count in enumerate(color_counts) if color != background))
    stats = SceneStats(
        height=int(height),
        width=int(width),
        background_color=int(background),
        color_counts=color_counts,
        non_background_count=non_background_count,
        component_count=len(components),
        unique_color_count=sum(1 for count in color_counts if count > 0),
        foreground_density=_safe_div(non_background_count, height * width),
    )
    return SceneAnalysis(stats=stats, components=tuple(components), labels=labels.copy())


def _simple_enclosed_background_count(
    grid: np.ndarray, background: int, min_r: int, min_c: int, max_r: int, max_c: int
) -> int:
    """Count bbox-background cells not connected to the bbox edge inside the bbox."""

    bbox = grid[min_r : max_r + 1, min_c : max_c + 1]
    bh, bw = bbox.shape
    background_mask = bbox == background
    if not background_mask.any():
        return 0

    exterior = np.zeros((bh, bw), dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for r in range(bh):
        for c in range(bw):
            on_edge = r == 0 or c == 0 or r == bh - 1 or c == bw - 1
            if on_edge and bool(background_mask[r, c]) and not bool(exterior[r, c]):
                exterior[r, c] = True
                queue.append((r, c))

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= bh or nc < 0 or nc >= bw:
                continue
            if bool(background_mask[nr, nc]) and not bool(exterior[nr, nc]):
                exterior[nr, nc] = True
                queue.append((nr, nc))

    return int(np.count_nonzero(background_mask & ~exterior))


def component_at_or_nearest(scene: SceneAnalysis, r: int, c: int) -> Component | None:
    """Return the component at ``(r, c)`` or the deterministic nearest component."""

    if not scene.components:
        return None

    clipped_r = int(np.clip(r, 0, scene.stats.height - 1))
    clipped_c = int(np.clip(c, 0, scene.stats.width - 1))
    label = int(scene.labels[clipped_r, clipped_c])
    if label >= 0:
        return scene.components[label]

    return min(
        scene.components,
        key=lambda component: (
            _component_distance(component, clipped_r, clipped_c),
            component.component_id,
            component.color,
        ),
    )


def _component_distance(component: Component, r: int, c: int) -> tuple[float, float]:
    min_r, min_c, max_r, max_c = component.bbox
    dr = 0.0 if min_r <= r <= max_r else float(min(abs(r - min_r), abs(r - max_r)))
    dc = 0.0 if min_c <= c <= max_c else float(min(abs(c - min_c), abs(c - max_c)))
    bbox_distance = float(np.hypot(dr, dc))
    centroid_distance = float(np.hypot(float(r) - component.centroid_r, float(c) - component.centroid_c))
    return bbox_distance, centroid_distance
