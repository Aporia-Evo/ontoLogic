"""Self-induced anonymous factor space from raw cell experience."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class RawObservation:
    pair_index: int
    side: int
    row_norm: float
    col_norm: float
    row_centered: float
    col_centered: float
    color_norm: float
    color_one_hot: tuple[float, ...] | None
    cell_index_norm: float


@dataclass(frozen=True)
class InducedFactorSpace:
    features: np.ndarray
    selected_candidate_indices: list[int]
    candidate_scores: list[float]
    redundancy_scores: list[float]
    compression_gain: float
    feature_width: int
    diagnostics: dict[str, Any]


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else float(num) / float(den)


def _norm_index(index: int, size: int) -> float:
    return _safe_div(index, size - 1)


def _centered_index(index: int, size: int) -> float:
    if size <= 1:
        return 0.0
    return (2.0 * float(index) / float(size - 1)) - 1.0


def _as_grid(value: Any) -> np.ndarray:
    arr = np.asarray(value, dtype=np.int64)
    if arr.ndim != 2 or arr.size == 0:
        raise ValueError("expected a non-empty 2D grid")
    if ((arr < 0) | (arr > 9)).any():
        raise ValueError("grid colors must be in 0..9")
    return arr


def _map_coordinate(r: int, c: int, from_dims: tuple[int, int], to_dims: tuple[int, int]) -> tuple[int, int]:
    if from_dims == to_dims:
        return r, c
    from_h, from_w = from_dims
    to_h, to_w = to_dims
    rr = int(round(_norm_index(r, from_h) * float(to_h - 1))) if to_h > 1 else 0
    cc = int(round(_norm_index(c, from_w) * float(to_w - 1))) if to_w > 1 else 0
    return int(np.clip(rr, 0, to_h - 1)), int(np.clip(cc, 0, to_w - 1))


def extract_raw_observations(task_or_pair: Any) -> np.ndarray:
    """Return raw primitive rows for train-pair output cells."""

    pairs = task_or_pair.get("train", [task_or_pair]) if isinstance(task_or_pair, dict) else [task_or_pair]
    rows: list[list[float]] = []
    for pair_index, pair in enumerate(pairs):
        if "input" not in pair or "output" not in pair:
            continue
        input_arr = _as_grid(pair["input"])
        output_arr = _as_grid(pair["output"])
        out_h, out_w = len(output_arr), len(output_arr[0])
        total = max(out_h * out_w - 1, 1)
        for r in range(out_h):
            for c in range(out_w):
                in_r, in_c = _map_coordinate(r, c, (out_h, out_w), (len(input_arr), len(input_arr[0])))
                color = int(input_arr[in_r, in_c])
                rows.append([
                    float(pair_index),
                    1.0,
                    _norm_index(r, out_h),
                    _norm_index(c, out_w),
                    _centered_index(r, out_h),
                    _centered_index(c, out_w),
                    _safe_div(color, 9.0),
                    *[float(color == k) for k in range(10)],
                    _safe_div(r * out_w + c, total),
                ])
    if not rows:
        raise ValueError("no raw observations extracted")
    return np.asarray(rows, dtype=np.float64)


class FactorInducer:
    def __init__(
        self,
        n_candidates: int = 256,
        n_survivors: int = 32,
        seed: int = 0,
        sparsity_weight: float = 0.001,
        complexity_weight: float = 0.001,
    ) -> None:
        if n_candidates < 1 or n_survivors < 1:
            raise ValueError("candidate and survivor counts must be positive")
        self.n_candidates = int(n_candidates)
        self.n_survivors = int(n_survivors)
        self.seed = int(seed)
        self.sparsity_weight = float(sparsity_weight)
        self.complexity_weight = float(complexity_weight)

    def induce(self, raw_observations, targets, groups) -> InducedFactorSpace:
        raw = np.asarray(raw_observations, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64).ravel()
        g = np.asarray(groups, dtype=np.int64).ravel()
        if raw.ndim != 2 or len(raw) != len(y) or len(y) != len(g):
            raise ValueError("raw observations, targets, and groups must be aligned")
        candidates, costs = self._candidate_matrix(raw)
        base = _loo_constant_surprise(y, g)
        scored: list[tuple[float, int, float]] = []
        for idx in range(len(candidates[0])):
            value = _loo_candidate_surprise(candidates[:, idx], y, g)
            gain = base - value - self.complexity_weight * costs[idx]
            gain -= self.sparsity_weight * float(np.mean(np.abs(candidates[:, idx]) > 1e-9))
            scored.append((float(gain), idx, float(value)))
        scored.sort(key=lambda item: (-item[0], item[1]))
        selected: list[int] = []
        redundancies: list[float] = []
        for gain, idx, _ in scored:
            if gain <= 0.0 or len(selected) >= self.n_survivors:
                break
            redundancy = _max_abs_corr(candidates[:, idx], candidates[:, selected]) if selected else 0.0
            if redundancy >= 0.98:
                continue
            selected.append(idx)
            redundancies.append(float(redundancy))
        features = candidates[:, selected] if selected else np.zeros((len(raw), 0), dtype=np.float64)
        gains = [item[0] for item in scored]
        mean_gain = float(np.mean([max(0.0, gains[i]) for i, idx in enumerate([s[1] for s in scored]) if idx in selected])) if selected else 0.0
        return InducedFactorSpace(
            features=features,
            selected_candidate_indices=selected,
            candidate_scores=gains,
            redundancy_scores=redundancies,
            compression_gain=mean_gain,
            feature_width=int(len(features[0]) if len(features) else 0),
            diagnostics={"base_surprise": float(base), "selected_factor_count": len(selected), "seed": self.seed},
        )

    def _candidate_matrix(self, raw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(self.seed)
        n, d = len(raw), len(raw[0])
        cols: list[np.ndarray] = []
        costs: list[float] = []
        while len(cols) < self.n_candidates:
            kind = len(cols) % 4
            if kind == 0:
                w = rng.normal(size=d)
                active = rng.random(d) < 0.35
                if active.any():
                    w = w * active
                col = raw @ w
                costs.append(float(np.count_nonzero(w)) / max(d, 1))
            elif kind == 1:
                a, b = rng.integers(0, d, size=2)
                col = raw[:, a] * raw[:, b]
                costs.append(2.0 / max(d, 1))
            elif kind == 2:
                w = rng.normal(size=d)
                phase = rng.uniform(0.0, 2.0 * np.pi)
                col = np.sin(raw @ w + phase)
                costs.append(1.0)
            else:
                w = rng.normal(size=d)
                active = rng.random(d) < 0.2
                if active.any():
                    w = w * active
                projection = raw @ w
                cut = float(np.median(projection))
                col = (projection > cut).astype(np.float64)
                costs.append(float(np.count_nonzero(w)) / max(d, 1))
            cols.append(_standardize(col))
        return np.column_stack(cols), np.asarray(costs, dtype=np.float64)


def _standardize(col: np.ndarray) -> np.ndarray:
    col = np.asarray(col, dtype=np.float64).ravel()
    scale = float(np.std(col))
    if scale <= 1e-12:
        return np.zeros_like(col)
    return (col - float(np.mean(col))) / scale


def _loo_constant_surprise(y: np.ndarray, g: np.ndarray) -> float:
    vals = []
    for held in np.unique(g):
        train = y[g != held]
        held_y = y[g == held]
        mean = float(np.mean(train)) if train.size else float(np.mean(y))
        vals.append(float(np.mean((held_y - mean) ** 2)))
    return float(np.mean(vals))


def _loo_candidate_surprise(x: np.ndarray, y: np.ndarray, g: np.ndarray) -> float:
    vals = []
    for held in np.unique(g):
        train = g != held
        test = g == held
        tx = np.column_stack([np.ones(np.count_nonzero(train)), x[train]])
        ty = y[train]
        ridge = np.diag([0.0, 1e-3])
        coef = np.linalg.pinv(tx.T @ tx + ridge) @ tx.T @ ty
        hx = np.column_stack([np.ones(np.count_nonzero(test)), x[test]])
        vals.append(float(np.mean((y[test] - hx @ coef) ** 2)))
    return float(np.mean(vals))


def _max_abs_corr(x: np.ndarray, mat: np.ndarray) -> float:
    if mat.size == 0:
        return 0.0
    x = _standardize(x)
    m = np.apply_along_axis(_standardize, 0, mat)
    return float(np.max(np.abs((x[:, None] * m).mean(axis=0))))
