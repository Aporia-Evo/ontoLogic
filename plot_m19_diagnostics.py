"""Static M19 diagnostic plotting utilities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


def load_json(path: str | Path) -> dict:
    """Load a JSON report from disk."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def plot_evolution_fitness(report: dict, out_dir: Path, svg: bool = False) -> list[Path]:
    rows = _evolution_rows(report)
    generations = _number_series(rows, "generation")
    best = _number_series(rows, "best_fitness")
    avg = _number_series(rows, "mean_fitness")
    if not generations or not best or not avg:
        _warn("skipping evolution_fitness: missing generation, best_fitness, or mean_fitness")
        return []
    plt = _pyplot()
    fig, ax = plt.subplots()
    ax.plot(generations[: len(best)], best, marker="o", label="best_fitness")
    ax.plot(generations[: len(avg)], avg, marker="o", label="mean_fitness")
    ax.set_xlabel("generation")
    ax.set_ylabel("fitness")
    ax.set_title("M19 factor induction fitness over generations")
    ax.legend()
    return _save(fig, out_dir, "evolution_fitness", svg)


def plot_evolution_behavior(report: dict, out_dir: Path, svg: bool = False) -> list[Path]:
    rows = _evolution_rows(report)
    generations = _number_series(rows, "generation")
    rel = _first_number_series(rows, ("mean_relative_improvement", "relative_improvement"))
    ceil = _first_number_series(rows, ("mean_ceiling_rate", "ceiling_rate"))
    max_order = _first_number_series(rows, ("mean_max_order_rate", "max_order_rate"))
    if not generations or not (rel or ceil or max_order):
        _warn("skipping evolution_behavior: missing behavior series")
        return []
    plt = _pyplot()
    fig, ax = plt.subplots()
    if rel:
        ax.plot(generations[: len(rel)], rel, marker="o", label="mean_relative_improvement")
    if ceil:
        ax.plot(generations[: len(ceil)], ceil, marker="o", label="mean_ceiling_rate")
    if max_order:
        ax.plot(generations[: len(max_order)], max_order, marker="o", label="mean_max_order_rate")
    ax.set_xlabel("generation")
    ax.set_ylabel("diagnostic value")
    ax.set_title("M19 diagnostic behavior over evolution")
    ax.legend()
    return _save(fig, out_dir, "evolution_behavior", svg)


def plot_finalist_fitness(report: dict, out_dir: Path, top: int = 10, svg: bool = False) -> list[Path]:
    rows = _finalist_rows(report)
    ranked = _top_by(rows, "fitness", top)
    if not ranked:
        _warn("skipping finalist_fitness: missing finalist fitness")
        return []
    labels = [_short_label(row, i) for i, row in enumerate(ranked, start=1)]
    values = [float(row["fitness"]) for row in ranked]
    plt = _pyplot()
    fig, ax = plt.subplots()
    ax.barh(labels, values)
    ax.invert_yaxis()
    ax.set_xlabel("fitness")
    ax.set_ylabel("genome")
    ax.set_title("Top M19 induced factor genomes")
    return _save(fig, out_dir, "finalist_fitness", svg)


def plot_finalist_complexity(report: dict, out_dir: Path, top: int = 25, svg: bool = False) -> list[Path]:
    rows = _top_by(_finalist_rows(report), "fitness", top)
    points = [
        (float(_first_present(row, ("mean_selected_factor_count", "selected_factor_count"))), float(row["fitness"]))
        for row in rows
        if _first_present(row, ("mean_selected_factor_count", "selected_factor_count")) is not None and _is_number(row.get("fitness"))
    ]
    if not points:
        _warn("skipping finalist_complexity: missing selected factor count or fitness")
        return []
    plt = _pyplot()
    fig, ax = plt.subplots()
    ax.scatter([p[0] for p in points], [p[1] for p in points])
    ax.set_xlabel("mean_selected_factor_count")
    ax.set_ylabel("fitness")
    ax.set_title("M19 fitness vs selected factor count")
    return _save(fig, out_dir, "finalist_complexity", svg)


def plot_ablation_deltas(report: dict, out_dir: Path, top: int = 25, svg: bool = False) -> list[Path]:
    rows = _ablation_rows_with_deltas(report)
    ranked = [row for row in rows if _is_number(row.get("delta_relative_improvement_vs_basic"))]
    ranked = sorted(ranked, key=lambda row: float(row["delta_relative_improvement_vs_basic"]))[-top:]
    if not ranked:
        _warn("skipping ablation_deltas: missing relative-improvement deltas")
        return []
    labels = [_truncate(str(row.get("label") or row.get("name") or f"run_{i}")) for i, row in enumerate(ranked)]
    values = [float(row["delta_relative_improvement_vs_basic"]) for row in ranked]
    plt = _pyplot()
    fig, ax = plt.subplots()
    ax.barh(labels, values)
    ax.set_xlabel("delta_relative_improvement_vs_basic")
    ax.set_ylabel("run")
    ax.set_title("M19 induced factor improvement vs basic")
    return _save(fig, out_dir, "ablation_deltas", svg)


def plot_ablation_ceiling_delta(report: dict, out_dir: Path, top: int = 25, svg: bool = False) -> list[Path]:
    rows = _ablation_rows_with_deltas(report)
    ranked = [row for row in rows if _is_number(row.get("delta_ceiling_rate_vs_basic"))]
    ranked = sorted(ranked, key=lambda row: float(row["delta_ceiling_rate_vs_basic"]))[:top]
    if not ranked:
        _warn("skipping ablation_ceiling_delta: missing ceiling-rate deltas")
        return []
    labels = [_truncate(str(row.get("label") or row.get("name") or f"run_{i}")) for i, row in enumerate(ranked)]
    values = [float(row["delta_ceiling_rate_vs_basic"]) for row in ranked]
    plt = _pyplot()
    fig, ax = plt.subplots()
    ax.barh(labels, values)
    ax.set_xlabel("delta_ceiling_rate_vs_basic")
    ax.set_ylabel("run")
    ax.set_title("M19 ceiling-rate change vs basic")
    return _save(fig, out_dir, "ablation_ceiling_delta", svg)


def plot_seed_stability(report: dict, out_dir: Path, svg: bool = False) -> list[Path]:
    rows = [row for row in _run_rows(report) if _first_present(row, ("induced_seed", "seed")) is not None]
    rows = [row for row in rows if _is_number(row.get("mean_relative_improvement"))]
    if not rows:
        _warn("skipping seed_stability: missing seed runs")
        return []
    labels = [str(_first_present(row, ("induced_seed", "seed"))) for row in rows]
    rel = [float(row["mean_relative_improvement"]) for row in rows]
    ceiling = [float(row.get("ceiling_rate", 0.0)) if _is_number(row.get("ceiling_rate")) else 0.0 for row in rows]
    max_order = [float(row.get("max_order_rate", 0.0)) if _is_number(row.get("max_order_rate")) else 0.0 for row in rows]
    plt = _pyplot()
    fig, ax = plt.subplots()
    x = list(range(len(rows)))
    width = 0.25
    ax.bar([v - width for v in x], rel, width=width, label="mean_relative_improvement")
    ax.bar(x, ceiling, width=width, label="ceiling_rate")
    ax.bar([v + width for v in x], max_order, width=width, label="max_order_rate")
    ax.set_xticks(x, labels)
    ax.set_xlabel("induced seed")
    ax.set_ylabel("diagnostic value")
    ax.set_title("M19 seed stability")
    ax.legend()
    return _save(fig, out_dir, "seed_stability", svg)


def plot_regime_counts(report: dict, out_dir: Path, svg: bool = False) -> list[Path]:
    counts = _regime_counts(report)
    if not counts:
        _warn("skipping regime_counts: missing regime counts")
        return []
    labels = [_truncate(str(label), 32) for label in counts]
    values = [int(value) for value in counts.values()]
    plt = _pyplot()
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel("regime")
    ax.set_ylabel("count")
    ax.set_title("M19 regime distribution")
    fig.autofmt_xdate(rotation=30, ha="right")
    return _save(fig, out_dir, "regime_counts", svg)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create M19 diagnostic plots from JSON reports.")
    parser.add_argument("--evolution", help="Path to an M19 evolution JSON report")
    parser.add_argument("--ablation", help="Path to an M19 ablation JSON report")
    parser.add_argument("--out-dir", required=True, help="Directory for generated plot files")
    parser.add_argument("--svg", action="store_true", help="Also write SVG files")
    parser.add_argument("--top-finalists", type=int, default=10, help="Number of finalist bars")
    parser.add_argument("--top-runs", type=int, default=25, help="Number of ablation bars")
    args = parser.parse_args(argv)
    if not args.evolution and not args.ablation:
        parser.error("provide --evolution, --ablation, or both")
    out_dir = Path(args.out_dir)
    created: list[Path] = []
    if args.evolution:
        report = load_json(args.evolution)
        created += plot_evolution_fitness(report, out_dir, args.svg)
        created += plot_evolution_behavior(report, out_dir, args.svg)
        created += plot_finalist_fitness(report, out_dir, args.top_finalists, args.svg)
        created += plot_finalist_complexity(report, out_dir, max(args.top_finalists, 25), args.svg)
    if args.ablation:
        report = load_json(args.ablation)
        created += plot_seed_stability(report, out_dir, args.svg)
        created += plot_regime_counts(report, out_dir, args.svg)
        created += plot_ablation_deltas(report, out_dir, args.top_runs, args.svg)
        created += plot_ablation_ceiling_delta(report, out_dir, args.top_runs, args.svg)
    for path in created:
        print(path)


def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is required for plotting; install the plot extra") from exc
    return plt


def _save(fig, out_dir: Path, stem: str, svg: bool) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [out_dir / f"{stem}.png"]
    if svg:
        paths.append(out_dir / f"{stem}.svg")
    fig.tight_layout()
    for path in paths:
        fig.savefig(path)
    _pyplot().close(fig)
    return paths


def _warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def _evolution_rows(report: dict) -> list[dict[str, Any]]:
    for key in ("generations", "history", "evolution", "runs"):
        value = report.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def _finalist_rows(report: dict) -> list[dict[str, Any]]:
    for key in ("finalists", "finalist_genomes", "top_genomes", "best_genomes"):
        value = report.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def _run_rows(report: dict) -> list[dict[str, Any]]:
    value = report.get("runs")
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _number_series(rows: Iterable[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if _is_number(row.get(key))]


def _first_number_series(rows: Iterable[dict[str, Any]], keys: tuple[str, ...]) -> list[float]:
    values = []
    for row in rows:
        value = _first_present(row, keys)
        if _is_number(value):
            values.append(float(value))
    return values


def _first_present(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def _top_by(rows: list[dict[str, Any]], key: str, top: int) -> list[dict[str, Any]]:
    ranked = [row for row in rows if _is_number(row.get(key))]
    return sorted(ranked, key=lambda row: float(row[key]), reverse=True)[:top]


def _short_label(row: dict[str, Any], rank: int) -> str:
    label = row.get("label") or row.get("genome_label") or row.get("genome_id") or row.get("id") or f"rank_{rank}"
    return _truncate(str(label))


def _truncate(value: str, width: int = 36) -> str:
    return value if len(value) <= width else value[: max(0, width - 1)] + "…"


def _ablation_rows_with_deltas(report: dict) -> list[dict[str, Any]]:
    rows = [dict(row) for row in _run_rows(report)]
    base = next((row for row in rows if row.get("factor_mode") == "basic" or row.get("label") == "basic"), None)
    base_rel = base.get("mean_relative_improvement") if base else None
    base_ceiling = base.get("ceiling_rate") if base else None
    for row in rows:
        if "delta_relative_improvement_vs_basic" not in row and _is_number(row.get("mean_relative_improvement")) and _is_number(base_rel):
            row["delta_relative_improvement_vs_basic"] = float(row["mean_relative_improvement"]) - float(base_rel)
        if "delta_ceiling_rate_vs_basic" not in row and _is_number(row.get("ceiling_rate")) and _is_number(base_ceiling):
            row["delta_ceiling_rate_vs_basic"] = float(row["ceiling_rate"]) - float(base_ceiling)
    return rows


def _regime_counts(report: dict) -> dict[str, int]:
    summary = report.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("regime_counts"), dict):
        return {str(k): int(v) for k, v in summary["regime_counts"].items() if _is_number(v)}
    counts: dict[str, int] = {}
    for row in _run_rows(report):
        regime = row.get("regime")
        if regime is not None:
            counts[str(regime)] = counts.get(str(regime), 0) + 1
    return counts


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


if __name__ == "__main__":
    main()
