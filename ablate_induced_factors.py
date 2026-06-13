"""Ablation runner for M19 self-induced factor space."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

_REPO_ROOT = Path(__file__).parent.absolute()
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from arc_ontology_lab import run_lab
from ontologic_core.report_analysis import analyze_report


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _compact(label: str, report: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    summary = analysis.get("summary", {})
    meta = report.get("metadata", {})
    return {
        "label": label,
        "factor_mode": meta.get("factor_mode"),
        "regime": summary.get("regime"),
        "regime_counts": dict(Counter([summary.get("regime") or "unknown"])),
        "ceiling_rate": _finite(summary.get("ceiling_rate")),
        "max_order_rate": _finite(summary.get("max_order_rate")),
        "mean_relative_improvement": _finite(summary.get("mean_relative_improvement")),
        "seed_stability": None,
        "selected_factor_count": meta.get("selected_factor_count"),
        "compression_gain": meta.get("mean_compression_gain"),
        "induced_candidates": meta.get("induced_candidates"),
        "induced_survivors": meta.get("induced_survivors"),
        "induced_seed": meta.get("induced_seed"),
    }


def run_ablation(
    data: str | Path,
    *,
    limit: int | None,
    max_order: int,
    lambda_: float,
    margin: float,
    seeds: list[int],
    candidate_counts: list[int],
    survivor_counts: list[int],
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    base_report = run_lab(data, limit=limit, max_order=max_order, lambda_=lambda_, margin=margin, factor_mode="basic")
    runs.append(_compact("basic", base_report, analyze_report(base_report)))

    for seed in seeds:
        report = run_lab(data, limit=limit, max_order=max_order, lambda_=lambda_, margin=margin, factor_mode="induced", induced_seed=seed)
        runs.append(_compact(f"seed_{seed}", report, analyze_report(report)))
    for count in candidate_counts:
        report = run_lab(data, limit=limit, max_order=max_order, lambda_=lambda_, margin=margin, factor_mode="induced", induced_candidates=count)
        runs.append(_compact(f"candidates_{count}", report, analyze_report(report)))
    for count in survivor_counts:
        report = run_lab(data, limit=limit, max_order=max_order, lambda_=lambda_, margin=margin, factor_mode="induced", induced_survivors=count)
        runs.append(_compact(f"survivors_{count}", report, analyze_report(report)))

    seed_values = [run.get("mean_relative_improvement") for run in runs if str(run.get("label", "")).startswith("seed_")]
    seed_values = [float(value) for value in seed_values if isinstance(value, int | float)]
    stability = 0.0 if len(seed_values) < 2 else float(pstdev(seed_values))
    for run in runs:
        if str(run.get("label", "")).startswith("seed_"):
            run["seed_stability"] = stability

    regimes = Counter(str(run.get("regime") or "unknown") for run in runs)
    induced = [run for run in runs if run.get("factor_mode") == "induced"]
    return {
        "summary": {
            "regime_counts": dict(sorted(regimes.items())),
            "ceiling_rate": mean([run["ceiling_rate"] for run in induced if run.get("ceiling_rate") is not None]) if induced else None,
            "max_order_rate": mean([run["max_order_rate"] for run in induced if run.get("max_order_rate") is not None]) if induced else None,
            "mean_relative_improvement": mean([run["mean_relative_improvement"] for run in induced if run.get("mean_relative_improvement") is not None]) if induced else None,
            "seed_stability": stability,
            "selected_factor_count": mean([run["selected_factor_count"] for run in induced if isinstance(run.get("selected_factor_count"), int | float)]) if induced else None,
            "compression_gain": mean([run["compression_gain"] for run in induced if isinstance(run.get("compression_gain"), int | float)]) if induced else None,
        },
        "runs": runs,
    }


def _int_list(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="M19 induced factor ablation")
    parser.add_argument("--data", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-order", type=int, default=3)
    parser.add_argument("--lambda", dest="lambda_", type=float, default=1.0)
    parser.add_argument("--margin", type=float, default=0.02)
    parser.add_argument("--seeds", type=_int_list, default=[0, 1, 2])
    parser.add_argument("--candidate-counts", type=_int_list, default=[64, 128, 256])
    parser.add_argument("--survivor-counts", type=_int_list, default=[8, 16, 32])
    parser.add_argument("--json-out", default="ablate_induced_factors.json")
    args = parser.parse_args(argv)
    report = run_ablation(
        args.data,
        limit=args.limit if args.limit > 0 else None,
        max_order=args.max_order,
        lambda_=args.lambda_,
        margin=args.margin,
        seeds=args.seeds,
        candidate_counts=args.candidate_counts,
        survivor_counts=args.survivor_counts,
    )
    Path(args.json_out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
