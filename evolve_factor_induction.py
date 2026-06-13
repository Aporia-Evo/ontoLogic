"""Evolution runner for M19 induced factor diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

_REPO_ROOT = Path(__file__).absolute().parent
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from arc_ontology_lab import run_lab
from ontologic_core.report_analysis import analyze_report

GENOME_FIELDS = (
    "induced_candidates",
    "induced_survivors",
    "induced_projection_sparsity",
    "induced_interaction_fraction",
    "induced_threshold_fraction",
    "induced_fourier_fraction",
    "induced_complexity_weight",
    "induced_redundancy_weight",
    "induced_stability_weight",
    "induced_max_feature_width",
    "induced_seed",
)

_GOOD_REGIMES = {"healthy_adaptive", "under_climbing", "ceiling_dominated"}


def _finite(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, int | float) and math.isfinite(float(value)):
        return float(value)
    return default


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(val) for key, val in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def _parse_float_list(raw: str) -> list[float]:
    values = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one value is required")
    return values


def _parse_slice_mode(raw: str) -> list[tuple[str, int, int | None]]:
    slices: list[tuple[str, int, int | None]] = []
    for item in [part.strip() for part in raw.split(",") if part.strip()]:
        if item.startswith("first"):
            count = int(item[5:])
            slices.append((item, 0, count))
        elif item.startswith("next"):
            count = int(item[4:])
            start = slices[-1][1] + int(slices[-1][2] or 0) if slices else count
            slices.append((item, start, count))
        elif item == "all":
            slices.append((item, 0, None))
        else:
            raise argparse.ArgumentTypeError(f"unsupported slice mode: {item}")
    return slices or [("all", 0, None)]


def _task_paths(data: str | Path) -> list[Path]:
    data_path = Path(data)
    if not data_path.exists() or not data_path.is_dir():
        raise FileNotFoundError(f"data path does not exist: {data_path}")
    return sorted(data_path.glob("*.json"))


def _slice_dir(paths: list[Path], start: int, count: int | None, parent: Path) -> Path:
    selected = paths[start:] if count is None else paths[start : start + count]
    out = parent / f"slice_{start}_{'all' if count is None else count}"
    out.mkdir(parents=True, exist_ok=True)
    for idx, src in enumerate(selected):
        shutil.copyfile(src, out / f"{idx:05d}_{src.name}")
    return out


def _initial_genome(rng: np.random.Generator, base_seed: int) -> dict[str, Any]:
    candidates = int(rng.choice([32, 64, 96, 128, 192, 256]))
    survivors = int(rng.choice([4, 8, 12, 16, 24, 32]))
    survivors = min(survivors, candidates)
    return {
        "induced_candidates": candidates,
        "induced_survivors": survivors,
        "induced_projection_sparsity": float(rng.uniform(0.15, 0.65)),
        "induced_interaction_fraction": float(rng.uniform(0.10, 0.45)),
        "induced_threshold_fraction": float(rng.uniform(0.10, 0.45)),
        "induced_fourier_fraction": float(rng.uniform(0.05, 0.35)),
        "induced_complexity_weight": float(10 ** rng.uniform(-4.0, -1.0)),
        "induced_redundancy_weight": float(rng.uniform(0.0, 0.25)),
        "induced_stability_weight": float(rng.uniform(0.0, 0.25)),
        "induced_max_feature_width": int(rng.choice([8, 12, 16, 24, 32, 48])),
        "induced_seed": int(base_seed + rng.integers(0, 100000)),
    }


def _mutate(genome: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    child = dict(genome)
    child["induced_candidates"] = int(np.clip(child["induced_candidates"] + rng.choice([-32, -16, 0, 16, 32]), 16, 512))
    child["induced_survivors"] = int(np.clip(child["induced_survivors"] + rng.choice([-4, -2, 0, 2, 4]), 2, child["induced_candidates"]))
    for key in (
        "induced_projection_sparsity",
        "induced_interaction_fraction",
        "induced_threshold_fraction",
        "induced_fourier_fraction",
        "induced_redundancy_weight",
        "induced_stability_weight",
    ):
        child[key] = float(np.clip(float(child[key]) + rng.normal(0.0, 0.05), 0.0, 1.0))
    child["induced_complexity_weight"] = float(np.clip(float(child["induced_complexity_weight"]) * math.exp(rng.normal(0.0, 0.5)), 1e-5, 1.0))
    child["induced_max_feature_width"] = int(np.clip(child["induced_max_feature_width"] + rng.choice([-4, 0, 4]), 2, 128))
    child["induced_seed"] = int(child["induced_seed"] + rng.integers(1, 997))
    return child


def _compact_metrics(reports: list[dict[str, Any]], analyses: list[dict[str, Any]], failures: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for report, analysis in zip(reports, analyses):
        summary = analysis.get("summary", {})
        meta = report.get("metadata", {})
        rows.append(
            {
                "regime": summary.get("regime"),
                "mean_relative_improvement": _finite(summary.get("mean_relative_improvement")),
                "ceiling_rate": _finite(summary.get("ceiling_rate")),
                "max_order_rate": _finite(summary.get("max_order_rate")),
                "selected_feature_count": _finite(meta.get("selected_factor_count")),
                "tasks": int(summary.get("tasks") or 0),
                "errors": int(summary.get("errors") or 0),
            }
        )
    total_tasks = sum(row["tasks"] for row in rows)
    total_errors = sum(row["errors"] for row in rows) + failures
    regimes = Counter(str(row["regime"] or "unknown") for row in rows)
    return {
        "mean_relative_improvement": mean([row["mean_relative_improvement"] for row in rows]) if rows else 0.0,
        "mean_ceiling_rate": mean([row["ceiling_rate"] for row in rows]) if rows else 1.0,
        "mean_max_order_rate": mean([row["max_order_rate"] for row in rows]) if rows else 1.0,
        "error_rate": float(total_errors) / float(max(total_tasks + failures, 1)),
        "normalized_selected_feature_count": mean([row["selected_feature_count"] / 64.0 for row in rows]) if rows else 1.0,
        "regime_counts": dict(sorted(regimes.items())),
        "slice_improvements": [row["mean_relative_improvement"] for row in rows],
    }


def _instability_penalty(metrics: dict[str, Any]) -> float:
    improvements = [float(v) for v in metrics.get("slice_improvements", [])]
    penalty = 0.0
    if len(improvements) >= 2:
        spread = max(improvements) - min(improvements)
        penalty += max(0.0, spread - 0.10) * 0.75
        if max(improvements) > 0.05 and min(improvements) <= 0.005:
            penalty += 0.10
    counts = Counter(metrics.get("regime_counts", {}))
    if counts:
        dominant = max(counts, key=lambda key: counts[key])
        if dominant not in _GOOD_REGIMES:
            penalty += 0.15
        if len(counts) > 2:
            penalty += 0.05 * (len(counts) - 2)
    return float(penalty)


def _fitness(metrics: dict[str, Any]) -> float:
    instability = _instability_penalty(metrics)
    metrics["instability_penalty"] = instability
    return float(
        metrics["mean_relative_improvement"]
        - 0.50 * metrics["mean_ceiling_rate"]
        - 0.25 * metrics["mean_max_order_rate"]
        - 0.05 * metrics["error_rate"]
        - 0.02 * metrics["normalized_selected_feature_count"]
        - instability
    )


def evaluate_genome(
    genome: dict[str, Any],
    *,
    slice_dirs: list[tuple[str, Path]],
    max_order: int,
    lambdas: list[float],
    margins: list[float],
) -> tuple[float, dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    analyses: list[dict[str, Any]] = []
    failures = 0
    for _, slice_path in slice_dirs:
        for lambda_ in lambdas:
            for margin in margins:
                try:
                    report = run_lab(
                        slice_path,
                        max_order=max_order,
                        lambda_=lambda_,
                        margin=margin,
                        factor_mode="induced",
                        induced_candidates=int(genome["induced_candidates"]),
                        induced_survivors=int(min(genome["induced_survivors"], genome["induced_max_feature_width"])),
                        induced_seed=int(genome["induced_seed"]),
                    )
                    reports.append(report)
                    analyses.append(analyze_report(report))
                except Exception:
                    failures += 1
    metrics = _compact_metrics(reports, analyses, failures)
    return _fitness(metrics), metrics


def run_evolution(
    data: str | Path,
    *,
    limit: int | None,
    generations: int,
    population: int,
    max_order: int,
    seed: int,
    elite_count: int,
    slice_mode: str,
    lambdas: list[float],
    margins: list[float],
) -> dict[str, Any]:
    paths = _task_paths(data)
    if limit is not None and limit > 0:
        paths = paths[:limit]
    if not paths:
        raise ValueError("data path contains no JSON tasks")
    rng = np.random.default_rng(seed)
    elite_count = max(1, min(int(elite_count), int(population)))
    population_rows = [_initial_genome(rng, seed) for _ in range(population)]
    history: list[dict[str, Any]] = []
    finalists: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="onto_m19_evolve_") as tmp:
        tmp_path = Path(tmp)
        slice_dirs = [(label, _slice_dir(paths, start, count, tmp_path)) for label, start, count in _parse_slice_mode(slice_mode)]
        for generation in range(generations):
            scored: list[dict[str, Any]] = []
            for genome in population_rows:
                try:
                    fit, metrics = evaluate_genome(
                        genome,
                        slice_dirs=slice_dirs,
                        max_order=max_order,
                        lambdas=lambdas,
                        margins=margins,
                    )
                except Exception as exc:
                    metrics = {"error_rate": 1.0, "message": type(exc).__name__}
                    fit = -1.0
                scored.append({"genome": dict(genome), "fitness": float(fit), "metrics": metrics})
            scored.sort(key=lambda item: item["fitness"], reverse=True)
            finalists = scored[: max(elite_count, min(5, population))]
            history.append(
                {
                    "generation": generation,
                    "best_fitness": float(scored[0]["fitness"]),
                    "mean_fitness": float(mean([row["fitness"] for row in scored])),
                    "best_genome": dict(scored[0]["genome"]),
                    "best_metrics": dict(scored[0]["metrics"]),
                }
            )
            elites = [row["genome"] for row in scored[:elite_count]]
            next_rows = [dict(row) for row in elites]
            while len(next_rows) < population:
                parent = elites[int(rng.integers(0, len(elites)))]
                next_rows.append(_mutate(parent, rng))
            population_rows = next_rows
    best = finalists[0]
    stable = bool(best["metrics"].get("instability_penalty", 1.0) <= 0.15 and best["metrics"].get("error_rate", 1.0) <= 0.10)
    notes = ["fitness uses ontology diagnostics only", "factor mode is induced"]
    if not stable:
        notes.append("best finalist still shows instability or task errors")
    return _json_safe(
        {
            "summary": {
                "best_genome": best["genome"],
                "best_fitness": best["fitness"],
                "generations": generations,
                "population": population,
                "stable": stable,
                "notes": notes,
            },
            "generations": history,
            "finalists": finalists,
        }
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evolve M19 induced factor diagnostics")
    parser.add_argument("--data", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--generations", type=int, default=8)
    parser.add_argument("--population", type=int, default=16)
    parser.add_argument("--max-order", type=int, default=2)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--elite-count", type=int, default=4)
    parser.add_argument("--slice-mode", default="first50,next50")
    parser.add_argument("--lambdas", type=_parse_float_list, default=[0.1, 1.0, 10.0])
    parser.add_argument("--margins", type=_parse_float_list, default=[0.005, 0.02, 0.05])
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    report = run_evolution(
        args.data,
        limit=args.limit if args.limit > 0 else None,
        generations=args.generations,
        population=args.population,
        max_order=args.max_order,
        seed=args.seed,
        elite_count=args.elite_count,
        slice_mode=args.slice_mode,
        lambdas=args.lambdas,
        margins=args.margins,
    )
    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
