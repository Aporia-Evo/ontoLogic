"""Parameter-stability analysis for ontology microscope runs.

This module only compares post-hoc run summaries produced from train-pair
structure diagnostics. It does not add task output construction or exact-match
selection.
"""

from __future__ import annotations

from collections import Counter
from math import isfinite
from statistics import mean
from typing import Any

CONSERVATIVE_ADJACENT_REGIMES = frozenset({"healthy_adaptive", "under_climbing"})
EXTREME_REGIMES = frozenset({"over_climbing", "ceiling_dominated"})


def summarize_sweep(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize stability across lambda/margin microscope settings."""

    regimes = [str(run.get("regime") or "unknown") for run in runs]
    regime_counts = dict(sorted(Counter(regimes).items()))
    dominant_regime = _dominant_regime(regime_counts)
    healthy_count = regime_counts.get("healthy_adaptive", 0)
    adjacent_count = sum(regime_counts.get(regime, 0) for regime in CONSERVATIVE_ADJACENT_REGIMES)
    extreme_present = {regime for regime in EXTREME_REGIMES if regime_counts.get(regime, 0) > 0}

    notes: list[str] = []
    if not runs:
        notes.append("no sweep runs were provided")
        return {
            "runs": 0,
            "stable_regime": False,
            "dominant_regime": None,
            "regime_counts": regime_counts,
            "notes": notes,
        }

    majority_threshold = len(runs) // 2 + 1
    stable_regime = adjacent_count >= majority_threshold and not _has_extreme_flip(extreme_present)

    if stable_regime:
        notes.append("most settings are healthy_adaptive or conservatively adjacent")
    if _has_extreme_flip(extreme_present):
        stable_regime = False
        notes.append("small parameter sweeps include both over_climbing and ceiling_dominated regimes")
    if healthy_count == 1 and len(runs) > 1:
        stable_regime = False
        notes.append("fragile: only one inspected setting is healthy_adaptive")
    if adjacent_count < majority_threshold:
        notes.append("fewer than half of settings are healthy_adaptive or conservatively adjacent")

    _append_numeric_notes(notes, runs)

    return {
        "runs": len(runs),
        "stable_regime": stable_regime,
        "dominant_regime": dominant_regime,
        "regime_counts": regime_counts,
        "notes": notes,
    }


def compact_run(
    lambda_value: float,
    margin: float,
    analysis: dict[str, Any],
    factor_mode: str | None = None,
    factor_groups: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Keep the sweep fields needed to compare one microscope setting."""

    summary = dict(analysis.get("summary") or {})
    run = {
        "lambda": float(lambda_value),
        "margin": float(margin),
        "regime": summary.get("regime"),
        "order_counts": dict(summary.get("order_counts") or {}),
        "ceiling_rate": _finite_or_none(summary.get("ceiling_rate")),
        "max_order_rate": _finite_or_none(summary.get("max_order_rate")),
        "mean_final_surprise": _finite_or_none(summary.get("mean_final_surprise")),
        "mean_relative_improvement": _finite_or_none(summary.get("mean_relative_improvement")),
    }
    if factor_mode is not None:
        run["factor_mode"] = factor_mode
    if factor_groups is not None:
        run["factor_groups"] = list(factor_groups)
    return run


def build_sweep_report(
    runs: list[dict[str, Any]],
    factor_mode: str | None = None,
    factor_groups: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Return the complete sweep JSON object."""

    report = {
        "summary": summarize_sweep(runs),
        "runs": runs,
    }
    metadata = {}
    if factor_mode is not None:
        metadata["factor_mode"] = factor_mode
    if factor_groups is not None:
        metadata["factor_groups"] = list(factor_groups)
    if metadata:
        report["metadata"] = metadata
    return report


def _dominant_regime(regime_counts: dict[str, int]) -> str | None:
    if not regime_counts:
        return None
    return min(regime_counts.items(), key=lambda item: (-item[1], item[0]))[0]


def _has_extreme_flip(extreme_present: set[str]) -> bool:
    return {"over_climbing", "ceiling_dominated"}.issubset(extreme_present)


def _append_numeric_notes(notes: list[str], runs: list[dict[str, Any]]) -> None:
    ceiling_values = [_as_float(run.get("ceiling_rate")) for run in runs]
    max_order_values = [_as_float(run.get("max_order_rate")) for run in runs]
    improvement_values = [_as_float(run.get("mean_relative_improvement")) for run in runs]

    ceiling_values = [value for value in ceiling_values if value is not None]
    max_order_values = [value for value in max_order_values if value is not None]
    improvement_values = [value for value in improvement_values if value is not None]

    if ceiling_values:
        notes.append(f"mean ceiling_rate across settings: {mean(ceiling_values):.3f}")
    if max_order_values:
        notes.append(f"mean max_order_rate across settings: {mean(max_order_values):.3f}")
    if improvement_values:
        notes.append(f"mean relative improvement across settings: {mean(improvement_values):.3f}")


def _finite_or_none(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if isfinite(value) else None
    return None


def _as_float(value: Any) -> float | None:
    finite = _finite_or_none(value)
    return float(finite) if finite is not None else None
