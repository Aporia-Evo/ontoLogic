"""CLI for M18 factor-group ablations over ontology microscope diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from math import isfinite
from pathlib import Path
from statistics import mean
from typing import Any

_REPO_ROOT = Path(__file__).parent.absolute()
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from arc_ontology_lab import _parse_factor_groups
from ontologic_core.arc_factors import BASIC_FACTOR_GROUP, HIERARCHICAL_FACTOR_GROUPS
from sweep_ontology_lab import _parse_float_list, run_sweep

_SELECTED_PAIR_GROUPS = (
    ("component_geometry", "component_bbox_relation"),
    ("component_geometry", "component_centroid_relation"),
    ("scene_stats", "global_geometry"),
    ("component_color", "component_rank"),
    ("local_density", "hole_or_enclosure"),
)
_EPSILON = 0.005
_MAX_ORDER_RATE_EXPLOSION = 0.20


def _mean_field(runs: list[dict[str, Any]], field: str) -> float | None:
    values = [run.get(field) for run in runs]
    finite = [float(value) for value in values if isinstance(value, int | float) and isfinite(float(value))]
    return mean(finite) if finite else None


def summarize_ablation_report(report: dict[str, Any]) -> dict[str, Any]:
    """Keep the comparison fields needed for one factor-group run."""

    summary = dict(report.get("summary") or {})
    runs = [run for run in list(report.get("runs") or []) if isinstance(run, dict)]
    return {
        "dominant_regime": summary.get("dominant_regime"),
        "regime_counts": dict(summary.get("regime_counts") or {}),
        "mean_ceiling_rate": _mean_field(runs, "ceiling_rate"),
        "mean_max_order_rate": _mean_field(runs, "max_order_rate"),
        "mean_relative_improvement": _mean_field(runs, "mean_relative_improvement"),
    }


def build_ablation_item(
    name: str,
    factor_mode: str,
    factor_groups: list[str],
    report: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Build one JSON row with deltas against the basic baseline."""

    summary = summarize_ablation_report(report)
    ceiling_delta = _delta(summary["mean_ceiling_rate"], baseline["mean_ceiling_rate"])
    improvement_delta = _delta(
        summary["mean_relative_improvement"], baseline["mean_relative_improvement"]
    )
    return {
        "name": name,
        "factor_mode": factor_mode,
        "factor_groups": factor_groups,
        **summary,
        "delta_ceiling_rate_vs_basic": ceiling_delta,
        "delta_relative_improvement_vs_basic": improvement_delta,
        "verdict": _verdict(summary, baseline, ceiling_delta, improvement_delta),
    }


def _delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None:
        return None
    return float(value - baseline)


def _verdict(
    summary: dict[str, Any],
    baseline: dict[str, Any],
    ceiling_delta: float | None,
    improvement_delta: float | None,
) -> str:
    if summary.get("dominant_regime") != "healthy_adaptive":
        return "unstable"
    max_order_rate = summary.get("mean_max_order_rate")
    baseline_max_order_rate = baseline.get("mean_max_order_rate")
    if isinstance(max_order_rate, int | float) and isinstance(baseline_max_order_rate, int | float):
        if float(max_order_rate) > float(baseline_max_order_rate) + _MAX_ORDER_RATE_EXPLOSION:
            return "unstable"
    if ceiling_delta is None or improvement_delta is None:
        return "neutral"
    if ceiling_delta > _EPSILON and improvement_delta < -_EPSILON:
        return "hurts"
    if ceiling_delta < -_EPSILON or improvement_delta > _EPSILON:
        return "helps"
    return "neutral"


def ablation_specs() -> list[tuple[str, str, list[str] | None]]:
    """Return deterministic M18 ablation specs after the basic baseline."""

    specs: list[tuple[str, str, list[str] | None]] = []
    for group in HIERARCHICAL_FACTOR_GROUPS:
        specs.append((group, "hierarchical", [group]))
    for group in HIERARCHICAL_FACTOR_GROUPS:
        specs.append((f"basic+{group}", "hierarchical", [BASIC_FACTOR_GROUP, group]))
    for first, second in _SELECTED_PAIR_GROUPS:
        specs.append(
            (
                f"basic+{first}+{second}",
                "hierarchical",
                [BASIC_FACTOR_GROUP, first, second],
            )
        )
    specs.append(("full_hierarchical", "hierarchical", None))
    return specs


def run_ablation(
    data: str | Path,
    *,
    limit: int | None,
    lambdas: list[float],
    margins: list[float],
    max_order: int,
) -> dict[str, Any]:
    baseline_report = run_sweep(
        data,
        limit=limit,
        lambdas=lambdas,
        margins=margins,
        max_order=max_order,
        factor_mode="basic",
        factor_groups=[BASIC_FACTOR_GROUP],
    )
    baseline = summarize_ablation_report(baseline_report)
    baseline.update(
        {
            "name": BASIC_FACTOR_GROUP,
            "factor_mode": "basic",
            "factor_groups": [BASIC_FACTOR_GROUP],
        }
    )

    runs = []
    for name, factor_mode, factor_groups in ablation_specs():
        report = run_sweep(
            data,
            limit=limit,
            lambdas=lambdas,
            margins=margins,
            max_order=max_order,
            factor_mode=factor_mode,
            factor_groups=factor_groups,
        )
        active_groups = list(report.get("metadata", {}).get("factor_groups") or factor_groups or [])
        runs.append(build_ablation_item(name, factor_mode, active_groups, report, baseline))

    return {"baseline": baseline, "runs": runs}


def write_report(report: dict[str, Any], json_out: str | Path) -> None:
    output_path = Path(json_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M18 factor-group ablation for ontology microscope diagnostics.")
    parser.add_argument("--data", required=True, help="Directory of ARC-style JSON tasks")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of task files to inspect; 0 means all")
    parser.add_argument("--max-order", type=int, default=2, help="Maximum interaction order for structure growth")
    parser.add_argument("--lambdas", type=_parse_float_list, required=True, help="Comma-separated lambda values")
    parser.add_argument("--margins", type=_parse_float_list, required=True, help="Comma-separated margin values")
    parser.add_argument("--factor-groups", type=_parse_factor_groups, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--json-out", default="arc_factor_group_ablation.json", help="Path for the ablation JSON report")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    limit = args.limit if args.limit > 0 else None
    report = run_ablation(
        args.data,
        limit=limit,
        lambdas=args.lambdas,
        margins=args.margins,
        max_order=args.max_order,
    )
    write_report(report, args.json_out)


if __name__ == "__main__":
    main()
