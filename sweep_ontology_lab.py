"""CLI for ontology-microscope lambda/margin stability sweeps."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from arc_ontology_lab import run_lab
from ontologic_core.report_analysis import analyze_report
from ontologic_core.sweep_analysis import build_run_record, build_sweep_report


def _parse_float_csv(text: str, *, name: str) -> list[float]:
    values: list[float] = []
    for raw in text.split(","):
        item = raw.strip()
        if not item:
            continue
        values.append(float(item))
    if not values:
        raise argparse.ArgumentTypeError(f"{name} needs at least one numeric value")
    return values


def run_sweep(
    data: str | Path,
    *,
    limit: int | None,
    lambdas: list[float],
    margins: list[float],
    max_order: int,
) -> dict:
    """Run lab diagnostics for each lambda/margin row and summarize stability."""

    rows = []
    for lambda_ in lambdas:
        for margin in margins:
            report = run_lab(data, limit=limit, max_order=max_order, lambda_=lambda_, margin=margin)
            analysis = analyze_report(report)
            rows.append(build_run_record(lambda_, margin, analysis))
    return build_sweep_report(rows)


def write_report(report: dict, json_out: str | Path) -> None:
    """Write a stable, indented JSON report."""

    output_path = Path(json_out)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sweep ontology microscope lambda/margin stability.")
    parser.add_argument("--data", required=True, help="Directory containing ARC-style JSON tasks.")
    parser.add_argument("--limit", type=int, default=None, help="Optional number of sorted tasks to inspect.")
    parser.add_argument("--lambdas", default="1.0", help="Comma-separated ridge lambda values.")
    parser.add_argument("--margins", default="0.02", help="Comma-separated structure-growth margins.")
    parser.add_argument("--max-order", type=int, default=3, help="Maximum interaction order for the gate.")
    parser.add_argument("--json-out", required=True, help="Path for the sweep JSON report.")
    args = parser.parse_args(argv)

    lambdas = _parse_float_csv(args.lambdas, name="--lambdas")
    margins = _parse_float_csv(args.margins, name="--margins")
    report = run_sweep(args.data, limit=args.limit, lambdas=lambdas, margins=margins, max_order=args.max_order)
    write_report(report, args.json_out)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
