"""Parameter-sweep summaries for the ontology microscope.

The sweep reads post-hoc diagnostic regimes across lambda/margin settings.  It
checks whether qualitative gate behavior is steady across nearby settings; it
does not choose settings from held-out exactness.
"""

from __future__ import annotations

from collections import Counter
from math import isfinite
from statistics import mean
from typing import Any

_CONSERVATIVE_ADJACENT = {"healthy_adaptive", "under_climbing"}
_OPPOSITE_EXTREMES = {"over_climbing", "ceiling_dominated"}


def build_run_record(lambda_: float, margin: float, analysis: dict[str, Any]) -> dict[str, Any]:
    """Convert one analysis object into the compact sweep row."""

    summary = dict(analysis.get("summary") or {})
    return {
        "lambda": float(lambda_),
        "margin": float(margin),
        "regime": str(summary.get("regime") or "insufficient_data"),
        "order_counts": dict(summary.get("order_counts") or {}),
        "ceiling_rate": _finite_float(summary.get("ceiling_rate"), default=0.0),
        "max_order_rate": _finite_float(summary.get("max_order_rate"), default=0.0),
        "mean_final_surprise": _finite_float(summary.get("mean_final_surprise"), default=None),
        "mean_relative_improvement": _finite_float(summary.get("mean_relative_improvement"), default=None),
    }


def summarize_sweep(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize regime stability across parameter rows."""

    regimes = [str(run.get("regime") or "insufficient_data") for run in runs]
    counts = Counter(regimes)
    dominant_regime = _dominant_regime(counts)
    healthy_count = counts.get("healthy_adaptive", 0)
    insufficient_count = counts.get("insufficient_data", 0)
    adjacent_count = sum(counts.get(regime, 0) for regime in _CONSERVATIVE_ADJACENT)
    narrow_healthy = healthy_count == 1 and len(runs) >= 3
    extreme_flip = all(counts.get(regime, 0) > 0 for regime in _OPPOSITE_EXTREMES)
    most_adjacent = bool(runs) and adjacent_count / len(runs) >= 0.67
    has_informative_row = bool(runs) and insufficient_count < len(runs)
    stable_regime = has_informative_row and most_adjacent and not narrow_healthy and not extreme_flip

    notes: list[str] = []
    if not runs:
        notes.append("no sweep rows were analyzed")
    if stable_regime:
        notes.append("most informative rows are healthy_adaptive or conservatively adjacent")
    if runs and insufficient_count == len(runs):
        notes.append("all rows are insufficient_data; parameter stability cannot be assessed")
    elif insufficient_count:
        notes.append(f"{insufficient_count} rows are insufficient_data and do not support stability")
    if extreme_flip:
        notes.append("rows include both over_climbing and ceiling_dominated regimes")
    if narrow_healthy:
        notes.append("healthy_adaptive appears in only one row")
    if not stable_regime and not notes:
        notes.append("regime mix is not stable across the requested settings")

    return {
        "runs": len(runs),
        "stable_regime": stable_regime,
        "dominant_regime": dominant_regime,
        "regime_counts": dict(counts),
        "notes": notes,
    }


def build_sweep_report(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the full JSON-ready sweep report."""

    return {
        "summary": summarize_sweep(runs),
        "runs": runs,
    }


def aggregate_numeric_field(runs: list[dict[str, Any]], field: str) -> float | None:
    """Mean of a numeric sweep field, ignoring absent values."""

    values = [_finite_float(run.get(field), default=None) for run in runs]
    present = [value for value in values if value is not None]
    return mean(present) if present else None


def _dominant_regime(counts: Counter[str]) -> str | None:
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _finite_float(value: Any, *, default: float | None) -> float | None:
    if isinstance(value, bool):
        return default
    if isinstance(value, int | float):
        numeric = float(value)
        return numeric if isfinite(numeric) else default
    return default
