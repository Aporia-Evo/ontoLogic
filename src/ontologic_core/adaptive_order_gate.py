"""Adaptive-order compositional gate for the Ontologic B-lane.

The gate grows structure from train-pair experience and chooses interaction
order by leave-one-out surprise/compression, not by task-level exact match.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement
from math import isfinite

import numpy as np

from .arc_factors import PairExperience


@dataclass(frozen=True)
class OrderCurvePoint:
    order: int
    surprise: float
    baseline_surprise: float
    complexity: float
    score: float
    num_features: int


@dataclass(frozen=True)
class GateDiagnosis:
    chosen_order: int | None
    cv_curve: list[OrderCurvePoint]
    ceiling_detected: bool
    selected_reason: str
    final_surprise: float
    final_complexity: float


class AdaptiveOrderGate:
    """Choose the least sufficient feature-interaction order from experience.

    The gate treats each :class:`PairExperience` as one train example group.  For
    each candidate order, it withholds one whole pair, fits a regularized linear
    model on the remaining pairs, and measures held-out surprise as mean squared
    prediction error.  Higher orders are accepted only when their penalized
    leave-one-out surprise improves by at least ``margin``.
    """

    def __init__(
        self,
        max_order: int = 3,
        lambda_: float = 1.0,
        margin: float = 0.02,
        complexity_weight: float = 0.002,
    ) -> None:
        if max_order < 1 or max_order > 3:
            raise ValueError("max_order must be between 1 and 3 for M16a")
        if lambda_ < 0:
            raise ValueError("lambda_ must be non-negative")
        if margin < 0:
            raise ValueError("margin must be non-negative")
        if complexity_weight < 0:
            raise ValueError("complexity_weight must be non-negative")
        self.max_order = max_order
        self.lambda_ = float(lambda_)
        self.margin = float(margin)
        self.complexity_weight = float(complexity_weight)

    def grow_structure(self, pairs: list[PairExperience]) -> GateDiagnosis:
        """Grow structure and choose the least sufficient interaction order.

        Selection uses only the provided train-pair experience.  A return value
        with ``ceiling_detected=True`` means that no learned order compressed the
        held-out surprise enough to beat the train-mean baseline.  In that case
        ``chosen_order`` is ``None`` because no order is justified by experience.
        """

        checked_pairs = _checked_pairs(pairs)
        baseline_surprise = _loo_baseline_surprise(checked_pairs)
        total_rows = sum(pair.features.shape[0] for pair in checked_pairs)

        cv_curve: list[OrderCurvePoint] = []
        for order in range(1, self.max_order + 1):
            expanded = [
                PairExperience(_expand_features(pair.features, order), pair.targets, pair.output_shape)
                for pair in checked_pairs
            ]
            surprise = _loo_ridge_surprise(expanded, self.lambda_)
            num_features = expanded[0].features.shape[1]
            complexity = self.complexity_weight * num_features / max(total_rows, 1)
            score = surprise + complexity
            cv_curve.append(
                OrderCurvePoint(
                    order=order,
                    surprise=surprise,
                    baseline_surprise=baseline_surprise,
                    complexity=complexity,
                    score=score,
                    num_features=num_features,
                )
            )

        chosen_point: OrderCurvePoint | None = None
        current_score = baseline_surprise
        selected_reason = "ceiling_detected: no learned order beat the baseline surprise"
        for point in cv_curve:
            if chosen_point is None:
                improvement = baseline_surprise - point.score
                if improvement <= self.margin:
                    continue
                chosen_point = point
                current_score = point.score
                selected_reason = (
                    f"order {point.order} accepted: penalized surprise beat the baseline "
                    f"by {improvement:.6g}, above margin {self.margin:.6g}"
                )
                continue

            improvement = current_score - point.score
            if improvement <= self.margin:
                break
            chosen_point = point
            current_score = point.score
            selected_reason = (
                f"order {point.order} accepted: penalized surprise improved "
                f"by {improvement:.6g}, above margin {self.margin:.6g}"
            )

        if chosen_point is None:
            return GateDiagnosis(
                chosen_order=None,
                cv_curve=cv_curve,
                ceiling_detected=True,
                selected_reason=selected_reason,
                final_surprise=baseline_surprise,
                final_complexity=0.0,
            )

        return GateDiagnosis(
            chosen_order=chosen_point.order,
            cv_curve=cv_curve,
            ceiling_detected=False,
            selected_reason=selected_reason,
            final_surprise=chosen_point.surprise,
            final_complexity=chosen_point.complexity,
        )


# Public helper: useful for focused tests and diagnostics, still train-only.
def expand_features(features: np.ndarray, order: int) -> np.ndarray:
    """Return a bias column plus all monomials up to the requested order."""

    return _expand_features(features, order)


def _checked_pairs(pairs: list[PairExperience]) -> list[PairExperience]:
    if len(pairs) < 2:
        raise ValueError("leave-one-out order selection needs at least two experience pairs")

    checked: list[PairExperience] = []
    target_width: int | None = None
    feature_width: int | None = None
    for pair in pairs:
        x = np.asarray(pair.features, dtype=np.float64)
        y = np.asarray(pair.targets, dtype=np.float64)
        if x.ndim != 2:
            raise ValueError(f"features must be a 2D matrix, got shape {x.shape}")
        if y.ndim == 1:
            y = y[:, None]
        if y.ndim != 2:
            raise ValueError(f"targets must be a 1D or 2D array, got shape {y.shape}")
        if x.shape[0] != y.shape[0]:
            raise ValueError("features and targets must have the same row count")
        if x.shape[0] == 0:
            raise ValueError("empty experience pairs are not supported")
        if feature_width is None:
            feature_width = x.shape[1]
        elif x.shape[1] != feature_width:
            raise ValueError("all experience pairs must have the same feature width")
        if target_width is None:
            target_width = y.shape[1]
        elif y.shape[1] != target_width:
            raise ValueError("all experience pairs must have the same target width")
        checked.append(PairExperience(x, y, pair.output_shape))
    return checked


def _expand_features(features: np.ndarray, order: int) -> np.ndarray:
    if order < 1 or order > 3:
        raise ValueError("feature expansion order must be 1, 2, or 3")
    x = np.asarray(features, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError(f"features must be a 2D matrix, got shape {x.shape}")

    columns = [np.ones((x.shape[0], 1), dtype=np.float64), x]
    n_features = x.shape[1]
    for degree in range(2, order + 1):
        products = []
        for indices in combinations_with_replacement(range(n_features), degree):
            term = np.prod(x[:, indices], axis=1, dtype=np.float64)
            products.append(term[:, None])
        if products:
            columns.append(np.hstack(products))
    return np.hstack(columns)


def _loo_baseline_surprise(pairs: list[PairExperience]) -> float:
    held_surprises: list[float] = []
    for held_index, held_pair in enumerate(pairs):
        train_y = np.vstack([pair.targets for i, pair in enumerate(pairs) if i != held_index])
        mean_y = train_y.mean(axis=0, keepdims=True)
        prediction = np.repeat(mean_y, held_pair.targets.shape[0], axis=0)
        held_surprises.append(_mse(held_pair.targets, prediction))
    return float(np.mean(held_surprises))


def _loo_ridge_surprise(pairs: list[PairExperience], lambda_: float) -> float:
    held_surprises: list[float] = []
    for held_index, held_pair in enumerate(pairs):
        train_x = np.vstack([pair.features for i, pair in enumerate(pairs) if i != held_index])
        train_y = np.vstack([pair.targets for i, pair in enumerate(pairs) if i != held_index])
        prediction = _ridge_predict(train_x, train_y, held_pair.features, lambda_)
        held_surprises.append(_mse(held_pair.targets, prediction))
    return float(np.mean(held_surprises))


def _ridge_predict(train_features: np.ndarray, train_targets: np.ndarray, held_features: np.ndarray, lambda_: float) -> np.ndarray:
    train_x = np.asarray(train_features, dtype=np.float64)
    if train_x.shape[1] > train_x.shape[0]:
        return _ridge_sample_space_predict(train_x, train_targets, held_features, lambda_)
    return _ridge_primal_predict(train_x, train_targets, held_features, lambda_)


def _ridge_primal_predict(
    train_features: np.ndarray, train_targets: np.ndarray, held_features: np.ndarray, lambda_: float
) -> np.ndarray:
    weights = _fit_ridge(train_features, train_targets, lambda_)
    return np.asarray(held_features, dtype=np.float64) @ weights


def _ridge_sample_space_predict(
    train_features: np.ndarray, train_targets: np.ndarray, held_features: np.ndarray, lambda_: float
) -> np.ndarray:
    train_x, train_y, held_x = _checked_ridge_arrays(train_features, train_targets, held_features, lambda_)
    x_body = train_x[:, 1:]
    held_body = held_x[:, 1:]
    x_mean = x_body.mean(axis=0, keepdims=True)
    y_mean = train_y.mean(axis=0, keepdims=True)
    train_centered = x_body - x_mean
    if train_centered.shape[1] == 0:
        return np.repeat(y_mean, held_x.shape[0], axis=0)

    lhs = train_centered @ train_centered.T + lambda_ * np.eye(train_centered.shape[0], dtype=np.float64)
    alpha = _linear_response(lhs, train_y - y_mean)
    slopes = train_centered.T @ alpha
    intercept = y_mean - x_mean @ slopes
    return intercept + held_body @ slopes


def _fit_ridge(features: np.ndarray, targets: np.ndarray, lambda_: float) -> np.ndarray:
    x, y, _ = _checked_ridge_arrays(features, targets, features, lambda_)
    penalty = lambda_ * np.eye(x.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.0  # do not regularize the bias column
    lhs = x.T @ x + penalty
    rhs = x.T @ y
    return _linear_response(lhs, rhs)


def _checked_ridge_arrays(
    train_features: np.ndarray, train_targets: np.ndarray, held_features: np.ndarray, lambda_: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    train_x = np.asarray(train_features, dtype=np.float64)
    train_y = np.asarray(train_targets, dtype=np.float64)
    held_x = np.asarray(held_features, dtype=np.float64)
    if train_y.ndim == 1:
        train_y = train_y[:, None]
    if train_x.ndim != 2 or held_x.ndim != 2:
        raise ValueError("ridge features must be 2D matrices")
    if train_y.ndim != 2:
        raise ValueError("ridge targets must be a 1D or 2D matrix")
    if train_x.shape[0] != train_y.shape[0]:
        raise ValueError("ridge features and targets must have the same row count")
    if train_x.shape[1] != held_x.shape[1]:
        raise ValueError("train and held feature widths must match")
    if train_x.shape[1] == 0:
        raise ValueError("ridge features need at least a bias column")
    if lambda_ < 0:
        raise ValueError("lambda_ must be non-negative")
    return train_x, train_y, held_x


def _linear_response(lhs: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    try:
        return np.linalg.lstsq(lhs, rhs, rcond=None)[0]
    except np.linalg.LinAlgError:
        return np.linalg.pinv(lhs) @ rhs


def _mse(targets: np.ndarray, predictions: np.ndarray) -> float:
    value = float(np.mean((targets - predictions) ** 2))
    if not isfinite(value):
        raise ValueError("surprise calculation produced a non-finite value")
    return value
