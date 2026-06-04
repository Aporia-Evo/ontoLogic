"""CLI for lambda/margin stability sweeps over ontology microscope diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.absolute()
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from arc_ontology_lab import run_lab
from ontologic_core.report_analysis import analyze_report
from ontologic_core.sweep_analysis import build_sweep_report, compact_run


def _parse_float_list(raw: str) -> list[float]:
    values = []
    for item in raw.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        values.append(float(stripped))
    if not values:
        raise argparse.ArgumentTypeError("at least one numeric value is required")
    return values


def run_sweep(
    data: str | Path,
    *,
    limit: int | None,
    lambdas: list[float],
    margins: list[float],
    max_order: int,
) -> dict:
    """Run the ontology microscope over each lambda/margin pair."""

    runs = []
    for lambda_value in lambdas:
        for margin in margins:
            report = run_lab(data, limit=limit, max_order=max_order, lambda_=lambda_value, margin=margin)
            analysis = analyze_report(report)
            runs.append(compact_run(lambda_value, margin, analysis))
    return build_sweep_report(runs)


def write_report(report: dict, json_out: str | Path) -> None:
    """Write stable, human-readable sweep JSON."""

    output_path = Path(json_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parameter-stability sweep for the ontology microscope.")
    parser.add_argument("--data", required=True, help="Directory of ARC-style JSON tasks")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of task files to inspect; 0 means all")
    parser.add_argument("--lambdas", type=_parse_float_list, required=True, help="Comma-separated lambda values")
    parser.add_argument("--margins", type=_parse_float_list, required=True, help="Comma-separated margin values")
    parser.add_argument("--max-order", type=int, default=3, help="Maximum interaction order for structure growth")
    parser.add_argument("--json-out", default="arc_ontology_sweep.json", help="Path for the sweep JSON report")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    limit = args.limit if args.limit > 0 else None
    report = run_sweep(args.data, limit=limit, lambdas=args.lambdas, margins=args.margins, max_order=args.max_order)
    write_report(report, args.json_out)


if __name__ == "__main__":
    main()
