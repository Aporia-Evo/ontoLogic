"""CLI entry point for ARC-as-ontology-microscope diagnostics.

The runner reports train-only structure-growth diagnostics for ARC-style JSON
files. It does not create predictions or optimize against held-out answers.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from ontologic_core.adaptive_order_gate import AdaptiveOrderGate, GateDiagnosis, OrderCurvePoint
from ontologic_core.arc_factors import (
    ALL_FACTOR_GROUPS,
    factor_group_widths,
    extract_task_experience,
    normalize_factor_groups,
    total_factor_width,
)

_FACTOR_MODES = ("basic", "hierarchical", "induced")
_FACTOR_GROUPS = ALL_FACTOR_GROUPS


def _finite_or_none(value: float | int | None) -> float | int | None:
    """Return JSON-safe finite numbers and replace non-finite values with null."""

    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _curve_point_to_json(point: OrderCurvePoint) -> dict[str, Any]:
    """Serialize one adaptive-order curve point."""

    return {
        "order": int(point.order),
        "surprise": _finite_or_none(float(point.surprise)),
        "baseline_surprise": _finite_or_none(float(point.baseline_surprise)),
        "complexity": _finite_or_none(float(point.complexity)),
        "score": _finite_or_none(float(point.score)),
        "num_features": int(point.num_features),
    }


def _diagnosis_to_json(task_name: str, diagnosis: GateDiagnosis) -> dict[str, Any]:
    """Serialize the diagnosis for one task."""

    return {
        "task": task_name,
        "status": "ok",
        "chosen_order": int(diagnosis.chosen_order) if diagnosis.chosen_order is not None else None,
        "ceiling_detected": bool(diagnosis.ceiling_detected),
        "selected_reason": str(diagnosis.selected_reason),
        "final_surprise": _finite_or_none(float(diagnosis.final_surprise)),
        "final_complexity": _finite_or_none(float(diagnosis.final_complexity)),
        "cv_curve": [_curve_point_to_json(point) for point in diagnosis.cv_curve],
    }


def diagnose_task(
    task_name: str,
    task: dict[str, Any],
    *,
    max_order: int,
    lambda_: float,
    margin: float,
    factor_mode: str = "basic",
    factor_groups: list[str] | tuple[str, ...] | None = None,
    induced_candidates: int = 256,
    induced_survivors: int = 32,
    induced_seed: int = 0,
) -> dict[str, Any]:
    """Extract train-pair experience and run train-only structure growth."""

    active_groups = _validate_factor_request(factor_mode, factor_groups)
    pairs = _extract_task_experience_with_mode(task, factor_mode, active_groups, induced_candidates, induced_survivors, induced_seed)
    gate = AdaptiveOrderGate(max_order=max_order, lambda_=lambda_, margin=margin)
    diagnosis = gate.grow_structure(pairs)
    detail = _diagnosis_to_json(task_name, diagnosis)
    detail["feature_width"] = int(pairs[0].features.shape[1])
    detail["factor_groups"] = list(active_groups)
    if factor_mode == "induced":
        diag = pairs[0].diagnostics or {}
        detail["selected_factor_count"] = int(diag.get("selected_factor_count", pairs[0].features.shape[1]))
        detail["mean_compression_gain"] = _finite_or_none(float(diag.get("compression_gain", 0.0)))
    return detail


def _error_detail(task_name: str, exc: Exception) -> dict[str, Any]:
    """Create a per-task error record without aborting the lab run."""

    return {
        "task": task_name,
        "status": "error",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "chosen_order": None,
        "ceiling_detected": False,
        "selected_reason": "error while diagnosing task",
        "final_surprise": None,
        "final_complexity": None,
        "cv_curve": [],
    }


def _mean(values: list[float]) -> float | None:
    """Return the arithmetic mean for a non-empty list, otherwise null."""

    if not values:
        return None
    return sum(values) / len(values)


def _summary(details: list[dict[str, Any]], max_order: int) -> dict[str, Any]:
    """Build the run summary from per-task diagnostics."""

    ok_details = [detail for detail in details if detail.get("status") == "ok"]
    order_counts = {str(order): 0 for order in range(1, max_order + 1)}
    order_counts["none"] = 0

    chosen_orders: list[float] = []
    final_surprises: list[float] = []
    final_complexities: list[float] = []

    for detail in ok_details:
        chosen_order = detail.get("chosen_order")
        if chosen_order is None:
            order_counts["none"] += 1
        else:
            order_key = str(chosen_order)
            if order_key not in order_counts:
                order_counts[order_key] = 0
            order_counts[order_key] += 1
            chosen_orders.append(float(chosen_order))

        final_surprise = detail.get("final_surprise")
        if isinstance(final_surprise, int | float):
            final_surprises.append(float(final_surprise))

        final_complexity = detail.get("final_complexity")
        if isinstance(final_complexity, int | float):
            final_complexities.append(float(final_complexity))

    return {
        "tasks": len(details),
        "ok": len(ok_details),
        "errors": len(details) - len(ok_details),
        "order_counts": order_counts,
        "ceiling_detected": sum(1 for detail in ok_details if detail.get("ceiling_detected")),
        "mean_chosen_order": _mean(chosen_orders),
        "mean_final_surprise": _mean(final_surprises),
        "mean_final_complexity": _mean(final_complexities),
    }


def _parse_factor_groups(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    groups = [item.strip() for item in raw.split(",") if item.strip()]
    if not groups:
        raise argparse.ArgumentTypeError("at least one factor group is required")
    return groups


def _validate_factor_request(
    factor_mode: str,
    factor_groups: list[str] | tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    if factor_mode not in _FACTOR_MODES:
        raise ValueError(f"factor_mode must be one of {_FACTOR_MODES}, got {factor_mode!r}")
    return normalize_factor_groups(factor_mode, factor_groups)


def _extract_task_experience_with_mode(
    task: dict[str, Any],
    factor_mode: str,
    factor_groups: tuple[str, ...],
    induced_candidates: int = 256,
    induced_survivors: int = 32,
    induced_seed: int = 0,
):
    try:
        return extract_task_experience(
            task,
            mode=factor_mode,
            factor_groups=factor_groups,
            induced_candidates=induced_candidates,
            induced_survivors=induced_survivors,
            induced_seed=induced_seed,
        )
    except TypeError as exc:
        if factor_mode == "basic" and factor_groups == ("basic",) and "mode" in str(exc):
            return extract_task_experience(task)
        raise


def run_lab(
    data: str | Path,
    *,
    limit: int | None = None,
    max_order: int = 3,
    lambda_: float = 1.0,
    margin: float = 0.02,
    factor_mode: str = "basic",
    factor_groups: list[str] | tuple[str, ...] | None = None,
    induced_candidates: int = 256,
    induced_survivors: int = 32,
    induced_seed: int = 0,
) -> dict[str, Any]:
    """Run ARC ontology microscope diagnostics over a directory of JSON tasks."""

    active_groups = _validate_factor_request(factor_mode, factor_groups)
    data_path = Path(data)
    task_paths = sorted(data_path.glob("*.json"))
    if limit is not None and limit > 0:
        task_paths = task_paths[:limit]

    details: list[dict[str, Any]] = []
    for task_path in task_paths:
        task_name = task_path.stem
        try:
            with task_path.open("r", encoding="utf-8") as handle:
                task = json.load(handle)
            details.append(
                diagnose_task(
                    task_name,
                    task,
                    max_order=max_order,
                    lambda_=lambda_,
                    margin=margin,
                    factor_mode=factor_mode,
                    factor_groups=active_groups,
                    induced_candidates=induced_candidates,
                    induced_survivors=induced_survivors,
                    induced_seed=induced_seed,
                )
            )
        except Exception as exc:  # keep one malformed task from aborting the lab run
            details.append(_error_detail(task_name, exc))

    metadata = {
        "factor_mode": factor_mode,
        "factor_groups": list(active_groups),
        "factor_group_widths": factor_group_widths(factor_mode, active_groups),
        "feature_width": details[0].get("feature_width") if details else total_factor_width(factor_mode, active_groups),
    }
    if factor_mode == "induced":
        gains = [float(d["mean_compression_gain"]) for d in details if isinstance(d.get("mean_compression_gain"), int | float)]
        counts = [float(d["selected_factor_count"]) for d in details if isinstance(d.get("selected_factor_count"), int | float)]
        metadata.update({
            "induced_candidates": induced_candidates,
            "induced_survivors": induced_survivors,
            "induced_seed": induced_seed,
            "selected_factor_count": _mean(counts),
            "mean_compression_gain": _mean(gains),
        })
    return {
        "metadata": metadata,
        "summary": _summary(details, max_order),
        "tasks_detail": details,
    }


def write_report(report: dict[str, Any], json_out: str | Path) -> None:
    """Write the lab report as stable, human-readable JSON."""

    output_path = Path(json_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for the ontology microscope."""

    parser = argparse.ArgumentParser(description="Ontologic B-lane ARC microscope diagnostic runner.")
    parser.add_argument("--data", required=True, help="Directory of ARC-style JSON tasks")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of task files to inspect; 0 means all")
    parser.add_argument("--max-order", type=int, default=3, help="Maximum interaction order for structure growth")
    parser.add_argument("--lambda", dest="lambda_", type=float, default=1.0, help="Complexity pressure used by the gate")
    parser.add_argument("--margin", type=float, default=0.02, help="Minimum improvement margin for order growth")
    parser.add_argument("--factor-mode", choices=_FACTOR_MODES, default="basic", help="ARC factor extraction mode")
    parser.add_argument("--induced-candidates", type=int, default=256, help="Number of anonymous candidate factors")
    parser.add_argument("--induced-survivors", type=int, default=32, help="Maximum anonymous induced factors to keep")
    parser.add_argument("--induced-seed", type=int, default=0, help="Seed for induced factor candidates")
    parser.add_argument(
        "--factor-groups",
        type=_parse_factor_groups,
        default=None,
        help="Comma-separated ARC factor groups; hierarchical mode uses all groups by default",
    )
    parser.add_argument("--json-out", default="arc_ontology_diag.json", help="Path for the diagnostic JSON report")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the lab CLI."""

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    report = run_lab(
        args.data,
        limit=args.limit,
        max_order=args.max_order,
        lambda_=args.lambda_,
        margin=args.margin,
        factor_mode=args.factor_mode,
        factor_groups=args.factor_groups,
        induced_candidates=args.induced_candidates,
        induced_survivors=args.induced_survivors,
        induced_seed=args.induced_seed,
    )
    write_report(report, args.json_out)


if __name__ == "__main__":
    main()
