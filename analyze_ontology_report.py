"""CLI entry point for ontology-lab report analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from ontologic_core.report_analysis import analyze_report, interesting_tasks


def read_report(path: str | Path) -> dict[str, Any]:
    """Read an ontology-lab diagnostic JSON report."""

    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_analysis(analysis: dict[str, Any], json_out: str | Path) -> None:
    """Write report analysis as stable, human-readable JSON."""

    output_path = Path(json_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(analysis, handle, indent=2, sort_keys=True)
        handle.write("\n")


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for report analysis."""

    parser = argparse.ArgumentParser(description="Analyze ontology-lab structure-growth diagnostics.")
    parser.add_argument("--report", required=True, help="Path to arc_ontology_diag.json")
    parser.add_argument("--json-out", default="arc_ontology_analysis.json", help="Path for analysis JSON")
    parser.add_argument("--top", type=int, default=20, help="Number of interesting tasks to include")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the report-analysis CLI."""

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    report = read_report(args.report)
    analysis = analyze_report(report)
    analysis["interesting_tasks"] = interesting_tasks(report.get("tasks_detail", []), limit=args.top)
    write_analysis(analysis, args.json_out)


if __name__ == "__main__":
    main()
