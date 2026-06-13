from __future__ import annotations

import ast
import json
from pathlib import Path

import arc_ontology_lab


def _write_task(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "train": [
                    {"input": [[0, 1], [0, 0]], "output": [[1, 0], [0, 1]]},
                    {"input": [[0, 2], [2, 0]], "output": [[2, 0], [0, 2]]},
                ],
                "test": [{"input": [[0, 1], [0, 0]]}],
            }
        ),
        encoding="utf-8",
    )


def test_run_lab_basic_factor_mode_records_metadata(tmp_path: Path) -> None:
    _write_task(tmp_path / "task.json")

    report = arc_ontology_lab.run_lab(tmp_path, factor_mode="basic")

    assert report["metadata"]["factor_mode"] == "basic"
    assert report["summary"]["tasks"] == 1
    assert report["tasks_detail"][0]["status"] == "ok"


def test_run_lab_hierarchical_factor_mode_records_metadata(tmp_path: Path) -> None:
    _write_task(tmp_path / "task.json")

    report = arc_ontology_lab.run_lab(tmp_path, factor_mode="hierarchical")

    assert report["metadata"]["factor_mode"] == "hierarchical"
    assert report["summary"]["tasks"] == 1
    assert report["tasks_detail"][0]["status"] == "ok"



def test_run_lab_records_factor_groups_and_widths(tmp_path: Path) -> None:
    _write_task(tmp_path / "task.json")

    report = arc_ontology_lab.run_lab(
        tmp_path,
        factor_mode="hierarchical",
        factor_groups=["basic", "component_geometry"],
    )

    assert report["metadata"]["factor_groups"] == ["basic", "component_geometry"]
    assert report["metadata"]["factor_group_widths"] == {"basic": 50, "component_geometry": 4}
    assert report["metadata"]["feature_width"] == 54
    assert report["tasks_detail"][0]["feature_width"] == 54


def test_no_output_construction_api_names_exist() -> None:
    source_paths = [
        Path("arc_ontology_lab.py"),
        Path("sweep_ontology_lab.py"),
        Path("src/ontologic_core/arc_factors.py"),
        Path("src/ontologic_core/arc_hierarchy.py"),
    ]
    forbidden_names = {"so" + "lve", "pre" + "dict"}
    for path in source_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert forbidden_names.isdisjoint(names)
