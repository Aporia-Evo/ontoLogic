"""Analysis layer for ontology-lab diagnostic reports.

This module reads structure-growth diagnostics and summarizes gate behavior.
It does not build held-out grids or change the adaptive-order gate.
"""

from __future__ import annotations

from collections import defaultdict
from math import isfinite
from statistics import mean
from typing import Any

REGIMES = {
    "healthy_adaptive",
    "over_climbing",
    "under_climbing",
    "ceiling_dominated",
    "too_many_errors",
    "insufficient_data",
}

_EPS = 1.0e-12


def analyze_report(report: dict) -> dict:
    """Summarize an ontology-lab diagnostic report.

    The expected input is the JSON object written by ``arc_ontology_lab.py``:
    a top-level ``summary`` and a ``tasks_detail`` list. The analysis is
    intentionally post-hoc: it only reads the recorded train-only diagnostics.
    """

    raw_tasks = list(report.get("tasks_detail", []))
    tasks_detail = [_derive_task_fields(task) for task in raw_tasks]
    ok_tasks = [task for task in tasks_detail if task.get("status") == "ok"]
    error_tasks = [task for task in tasks_detail if task.get("status") == "error"]

    max_order = _max_order_seen(tasks_detail)
    order_counts = _order_counts(ok_tasks, max_order)
    ceiling_count = sum(1 for task in ok_tasks if task.get("ceiling_detected"))
    max_order_count = sum(1 for task in ok_tasks if task.get("max_order_reached"))

    final_surprises = [_as_float(task.get("final_surprise")) for task in ok_tasks]
    relative_improvements = [_as_float(task.get("relative_improvement")) for task in ok_tasks]

    summary = {
        "tasks": len(tasks_detail),
        "ok": len(ok_tasks),
        "errors": len(error_tasks),
        "regime": "insufficient_data",
        "order_counts": order_counts,
        "ceiling_rate": _rate(ceiling_count, len(ok_tasks)),
        "max_order_rate": _rate(max_order_count, len(ok_tasks)),
        "mean_final_surprise": _mean_present(final_surprises),
        "mean_relative_improvement": _mean_present(relative_improvements),
        "mean_surprise_by_order": _mean_curve_field_by_order(ok_tasks, "surprise"),
        "mean_complexity_by_order": _mean_curve_field_by_order(ok_tasks, "complexity"),
    }
    summary["regime"] = classify_gate_regime(summary, tasks_detail)

    return {
        "summary": summary,
        "interpretation": _interpretation(summary),
        "interesting_tasks": interesting_tasks(tasks_detail),
    }


def classify_gate_regime(summary: dict, tasks_detail: list[dict]) -> str:
    """Classify the observed gate regime from aggregate diagnostics."""

    tasks = int(summary.get("tasks") or len(tasks_detail))
    ok = int(summary.get("ok") or sum(1 for task in tasks_detail if task.get("status") == "ok"))
    errors = int(summary.get("errors") or max(tasks - ok, 0))

    if ok < 5:
        return "insufficient_data"
    if tasks > 0 and errors / tasks > 0.25:
        return "too_many_errors"

    ceiling_rate = _as_float(summary.get("ceiling_rate"))
    if ceiling_rate is None:
        ceiling_rate = _rate(sum(1 for task in tasks_detail if task.get("status") == "ok" and task.get("ceiling_detected")), ok)
    if ceiling_rate > 0.60:
        return "ceiling_dominated"

    max_order_rate = _as_float(summary.get("max_order_rate"))
    if max_order_rate is None:
        max_order = _max_order_seen(tasks_detail)
        max_order_rate = _rate(
            sum(
                1
                for task in tasks_detail
                if task.get("status") == "ok" and task.get("chosen_order") == max_order and max_order is not None
            ),
            ok,
        )
    if max_order_rate > 0.50 and ceiling_rate < 0.20:
        return "over_climbing"

    order_counts = summary.get("order_counts") or {}
    order_one_count = int(order_counts.get("1") or 0)
    mean_final_surprise = _as_float(summary.get("mean_final_surprise"))
    baseline_values = [_as_float(task.get("baseline_surprise")) for task in tasks_detail if task.get("status") == "ok"]
    mean_baseline = _mean_present(baseline_values)
    mean_relative_improvement = _as_float(summary.get("mean_relative_improvement"))
    high_relative_to_baseline = False
    if mean_baseline is not None and mean_baseline > _EPS and mean_final_surprise is not None:
        high_relative_to_baseline = mean_final_surprise / mean_baseline > 0.80
    elif mean_relative_improvement is not None:
        high_relative_to_baseline = mean_relative_improvement < 0.20
    if order_one_count / ok > 0.75 and high_relative_to_baseline:
        return "under_climbing"

    used_orders = [order for order, count in order_counts.items() if order != "none" and count]
    errors_low = tasks == 0 or errors / tasks <= 0.25
    if len(used_orders) >= 2 and 0.0 < ceiling_rate <= 0.60 and max_order_rate <= 0.50 and errors_low:
        return "healthy_adaptive"
    if len(used_orders) >= 2 and max_order_rate <= 0.50 and errors_low:
        return "healthy_adaptive"

    return "under_climbing" if order_one_count / ok > 0.75 else "healthy_adaptive"


def interesting_tasks(tasks_detail: list[dict], limit: int = 20) -> list[dict]:
    """Return tasks worth inspecting after the aggregate report.

    Priority is given to ceilings, max-order selections, large compression of
    surprise, slight rejected improvements at higher order, and task errors.
    """

    enriched = [_derive_task_fields(task) for task in tasks_detail]
    candidates: list[tuple[float, dict[str, Any]]] = []
    for index, task in enumerate(enriched):
        reason, priority = _interesting_reason(task)
        if reason is None:
            continue
        item = {
            "task": task.get("task"),
            "reason": reason,
            "chosen_order": task.get("chosen_order"),
            "ceiling_detected": bool(task.get("ceiling_detected")),
            "relative_improvement": task.get("relative_improvement"),
            "selected_reason": task.get("selected_reason"),
        }
        if task.get("status") == "error":
            item["error_type"] = task.get("error_type")
            item["error"] = task.get("error")
        candidates.append((priority - index * 1.0e-6, item))

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in candidates[: max(limit, 0)]]


def _derive_task_fields(task: dict[str, Any]) -> dict[str, Any]:
    derived = dict(task)
    curve = [point for point in list(task.get("cv_curve") or []) if isinstance(point, dict)]
    max_order = _max_curve_order(curve)
    chosen_order = task.get("chosen_order")
    baseline_surprise = _baseline_surprise(task, curve)
    final_surprise = _as_float(task.get("final_surprise"))
    if final_surprise is None and chosen_order is not None:
        chosen_point = _curve_point(curve, chosen_order)
        final_surprise = _as_float(chosen_point.get("surprise")) if chosen_point else None

    absolute_improvement = None
    relative_improvement = None
    if baseline_surprise is not None and final_surprise is not None:
        absolute_improvement = baseline_surprise - final_surprise
        if abs(baseline_surprise) > _EPS:
            relative_improvement = absolute_improvement / abs(baseline_surprise)

    derived.update(
        {
            "best_order_by_score": _best_order_by_score(curve),
            "chosen_order": chosen_order,
            "ceiling_detected": bool(task.get("ceiling_detected")),
            "baseline_surprise": baseline_surprise,
            "final_surprise": final_surprise,
            "absolute_improvement": absolute_improvement,
            "relative_improvement": relative_improvement,
            "max_order_reached": chosen_order is not None and max_order is not None and chosen_order == max_order,
            "curve_monotonicity": _curve_monotonicity(curve),
            "selected_reason": task.get("selected_reason"),
            "higher_order_rejected_after_slight_gain": _higher_order_rejected_after_slight_gain(curve, chosen_order),
        }
    )
    return derived


def _interesting_reason(task: dict[str, Any]) -> tuple[str | None, float]:
    if task.get("status") == "error":
        return "task_error", 100.0
    if task.get("ceiling_detected"):
        return "ceiling_detected", 90.0
    if task.get("max_order_reached"):
        return "max_order_reached", 80.0
    rel = _as_float(task.get("relative_improvement"))
    if rel is not None and rel >= 0.40:
        return "large_surprise_improvement", 70.0 + min(rel, 1.0)
    if task.get("higher_order_rejected_after_slight_gain"):
        return "higher_order_rejected_after_slight_gain", 60.0
    return None, 0.0


def _interpretation(summary: dict[str, Any]) -> list[str]:
    regime = summary.get("regime")
    bullets = [f"regime: {regime}"]
    bullets.append(
        "order_distribution: "
        + ", ".join(f"order {order}={count}" for order, count in sorted(summary.get("order_counts", {}).items()))
    )
    ceiling_rate = summary.get("ceiling_rate")
    max_order_rate = summary.get("max_order_rate")
    bullets.append(f"ceiling rate is {_format_rate(ceiling_rate)}; max-order rate is {_format_rate(max_order_rate)}.")

    if regime == "over_climbing":
        bullets.append("The gate often grows to the maximum order without many ceilings; inspect whether complexity pressure is too weak.")
    elif regime == "under_climbing":
        bullets.append("The gate mostly stays at order 1 while surprise remains close to baseline; inspect whether factors are too weak or margin is too strict.")
    elif regime == "ceiling_dominated":
        bullets.append("Most inspected tasks hit ceilings, suggesting the current factors often cannot justify structure growth.")
    elif regime == "too_many_errors":
        bullets.append("Many task diagnostics errored; inspect data loading and factor extraction before interpreting structure_growth.")
    elif regime == "insufficient_data":
        bullets.append("Too few successful tasks were analyzed to infer a reliable gate regime.")
    else:
        bullets.append("The gate uses multiple orders without max-order dominance, consistent with conservative adaptive structure_growth.")
    return bullets


def _order_counts(tasks: list[dict[str, Any]], max_order: int | None) -> dict[str, int]:
    highest = max_order or 0
    counts = {str(order): 0 for order in range(1, highest + 1)}
    counts["none"] = 0
    for task in tasks:
        chosen = task.get("chosen_order")
        if chosen is None:
            counts["none"] += 1
        else:
            counts[str(chosen)] = counts.get(str(chosen), 0) + 1
    return counts


def _mean_curve_field_by_order(tasks: list[dict[str, Any]], field: str) -> dict[str, float | None]:
    values: dict[int, list[float]] = defaultdict(list)
    for task in tasks:
        for point in task.get("cv_curve") or []:
            order = point.get("order")
            value = _as_float(point.get(field))
            if isinstance(order, int) and value is not None:
                values[order].append(value)
    return {str(order): _mean_present(vals) for order, vals in sorted(values.items())}


def _best_order_by_score(curve: list[dict[str, Any]]) -> int | None:
    best_order = None
    best_value = None
    for point in curve:
        order = point.get("order")
        value = _as_float(point.get("score"))
        if value is None:
            value = _as_float(point.get("surprise"))
        if not isinstance(order, int) or value is None:
            continue
        if best_value is None or value < best_value:
            best_order = order
            best_value = value
    return best_order


def _higher_order_rejected_after_slight_gain(curve: list[dict[str, Any]], chosen_order: Any) -> bool:
    if not isinstance(chosen_order, int):
        return False
    chosen_point = _curve_point(curve, chosen_order)
    next_point = _curve_point(curve, chosen_order + 1)
    if not chosen_point or not next_point:
        return False
    chosen_score = _as_float(chosen_point.get("score"))
    next_score = _as_float(next_point.get("score"))
    if chosen_score is not None and next_score is not None and next_score < chosen_score:
        return True
    chosen_surprise = _as_float(chosen_point.get("surprise"))
    next_surprise = _as_float(next_point.get("surprise"))
    return chosen_surprise is not None and next_surprise is not None and next_surprise < chosen_surprise


def _curve_monotonicity(curve: list[dict[str, Any]]) -> str:
    values = [_as_float(point.get("surprise")) for point in sorted(curve, key=lambda point: point.get("order") or 0)]
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return "unknown"
    diffs = [values[index + 1] - values[index] for index in range(len(values) - 1)]
    if all(abs(diff) <= _EPS for diff in diffs):
        return "flat"
    if all(diff <= _EPS for diff in diffs):
        return "decreasing"
    if all(diff >= -_EPS for diff in diffs):
        return "increasing"
    return "mixed"


def _baseline_surprise(task: dict[str, Any], curve: list[dict[str, Any]]) -> float | None:
    value = _as_float(task.get("baseline_surprise"))
    if value is not None:
        return value
    for point in curve:
        value = _as_float(point.get("baseline_surprise"))
        if value is not None:
            return value
    return None


def _curve_point(curve: list[dict[str, Any]], order: Any) -> dict[str, Any] | None:
    for point in curve:
        if point.get("order") == order:
            return point
    return None


def _max_order_seen(tasks: list[dict[str, Any]]) -> int | None:
    orders = []
    for task in tasks:
        curve_max = _max_curve_order(task.get("cv_curve") or [])
        if curve_max is not None:
            orders.append(curve_max)
        chosen = task.get("chosen_order")
        if isinstance(chosen, int):
            orders.append(chosen)
    return max(orders) if orders else None


def _max_curve_order(curve: list[dict[str, Any]]) -> int | None:
    orders = [point.get("order") for point in curve if isinstance(point.get("order"), int)]
    return max(orders) if orders else None


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        numeric = float(value)
        return numeric if isfinite(numeric) else None
    return None


def _mean_present(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return mean(present) if present else None


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: Any) -> str:
    numeric = _as_float(value)
    return "n/a" if numeric is None else f"{numeric:.1%}"
