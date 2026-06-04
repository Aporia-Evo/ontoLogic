"""CLI entry point for ARC-as-ontology-microscope diagnostics.

This file must not create Kaggle submissions or optimise exact-match score.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Ontologic B-lane ARC microscope; not a solver.")
    parser.add_argument("--data", required=True, help="Directory of ARC-style JSON tasks")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-order", type=int, default=3)
    parser.add_argument("--lambda", dest="lambda_", type=float, default=1.0)
    parser.add_argument("--margin", type=float, default=0.02)
    parser.add_argument("--json-out", default="arc_ontology_diag.json")
    parser.parse_args()
    raise NotImplementedError("M16 microscope CLI is not implemented yet")


if __name__ == "__main__":
    main()
