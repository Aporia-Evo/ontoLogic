"""Adaptive-order compositional gate for the Ontologic B-lane.

The gate grows structure from experience and chooses interaction order by
train-only surprise/compression, not ARC score.
"""

from __future__ import annotations

from dataclasses import dataclass

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
    chosen_order: int
    cv_curve: list[OrderCurvePoint]
    ceiling_detected: bool
    selected_reason: str
    final_surprise: float
    final_complexity: float


class AdaptiveOrderGate:
    """Minimal API target for M16.

    Selection must use only train-pair experience. Post-hoc exact metrics belong
    outside this class.
    """

    def __init__(self, max_order: int = 3, lambda_: float = 1.0, margin: float = 0.02) -> None:
        self.max_order = max_order
        self.lambda_ = lambda_
        self.margin = margin

    def grow_structure(self, pairs: list[PairExperience]) -> GateDiagnosis:
        """Grow structure and choose least sufficient interaction order.

        TODO(M16): implement leave-one-out surprise, complexity pressure, adaptive
        order growth, and ceiling detection.
        """

        raise NotImplementedError("M16 adaptive-order gate is not implemented yet")
