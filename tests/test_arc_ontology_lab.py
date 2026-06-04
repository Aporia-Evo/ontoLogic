from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np

import arc_ontology_lab
from ontologic_core.adaptive_order_gate import GateDiagnosis, OrderCurvePoint
from ontologic_core.arc_factors import PairExperience


def _write_task(path: Path, test_output: int | None = 9) -> None:
    test_pair = {"input": [[1]]}
    if test_output is not None:
        test_pair["output"] = [[test_output]]
    path.write_text(
        json.dumps(
            {
                "train": [
                    {"input": [[1]], "output": [[2]]},
                    {"input": [[2]], "output": [[3]]},
                ],
                "test": [test_pair],
            }
        ),
        encoding="utf-8",
    )


def _fake_extract_task_experience(task: dict) -> list[PairExperience]:
    return [
        PairExperience(
            features=np.asarray(pair["input"], dtype=np.float64).reshape(1, -1),
            targets=np.asarray(pair["output"], dtype=np.float64).reshape(1),
            output_shape=(1, 1),
        )
        for pair in task["train"]
    ]


def _fake_grow_structure(self, pairs: list[PairExperience]) -> GateDiagnosis:
    train_total = sum(float(pair.features.sum() + pair.targets.sum()) for pair in pairs)
    chosen_order = 1 if train_total < 10 else 2
    return GateDiagnosis(
        chosen_order=chosen_order,
        cv_curve=[
            OrderCurvePoint(
                order=1,
                surprise=0.25,
                baseline_surprise=0.50,
                complexity=0.10,
                score=0.35,
                num_features=3,
            )
        ],
        ceiling_detected=False,
        selected_reason="train-pair experience selected least sufficient order",
        final_surprise=0.25,
        final_complexity=0.10,
    )


def test_run_lab_writes_diagnostic_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(arc_ontology_lab, "extract_task_experience", _fake_extract_task_experience)
    monkeypatch.setattr(arc_ontology_lab.AdaptiveOrderGate, "grow_structure", _fake_grow_structure)

    _write_task(tmp_path / "task_a.json")
    _write_task(tmp_path / "task_b.json")
    json_out = tmp_path / "arc_ontology_diag.json"

    report = arc_ontology_lab.run_lab(tmp_path, limit=2, max_order=3, lambda_=1.0, margin=0.02)
    arc_ontology_lab.write_report(report, json_out)

    loaded = json.loads(json_out.read_text(encoding="utf-8"))
    assert json_out.exists()
    assert loaded["summary"]["tasks"] == 2
    assert loaded["summary"]["ok"] == 2
    assert loaded["summary"]["errors"] == 0
    assert set(loaded["summary"]["order_counts"]) == {"1", "2", "3", "none"}
    assert loaded["tasks_detail"][0]["status"] == "ok"
    assert loaded["tasks_detail"][0]["cv_curve"][0]["order"] == 1


def test_test_output_is_not_required_and_does_not_change_choice(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(arc_ontology_lab, "extract_task_experience", _fake_extract_task_experience)
    monkeypatch.setattr(arc_ontology_lab.AdaptiveOrderGate, "grow_structure", _fake_grow_structure)

    _write_task(tmp_path / "with_test_output.json", test_output=9)
    _write_task(tmp_path / "without_test_output.json", test_output=None)

    report = arc_ontology_lab.run_lab(tmp_path, max_order=3)
    by_task = {detail["task"]: detail for detail in report["tasks_detail"]}

    assert report["summary"]["ok"] == 2
    assert by_task["with_test_output"]["chosen_order"] == by_task["without_test_output"]["chosen_order"]


def test_arc_ontology_lab_has_no_function_named_solve() -> None:
    source = Path(arc_ontology_lab.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "solve" not in function_names
