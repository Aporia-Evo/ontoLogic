from __future__ import annotations

import ast
from pathlib import Path

from ontologic_core.report_analysis import analyze_report, interesting_tasks


def _point(order: int, surprise: float, baseline: float = 1.0, complexity: float = 0.01) -> dict:
    return {
        "order": order,
        "surprise": surprise,
        "baseline_surprise": baseline,
        "complexity": complexity * order,
        "score": surprise + complexity * order,
        "num_features": order * 3,
    }


def _ok(task: str, chosen_order: int | None, *, ceiling: bool = False, values: tuple[float, float, float] = (0.7, 0.5, 0.45)) -> dict:
    final = 1.0 if chosen_order is None else values[chosen_order - 1]
    return {
        "task": task,
        "status": "ok",
        "chosen_order": chosen_order,
        "ceiling_detected": ceiling,
        "selected_reason": "synthetic structure_growth diagnostic",
        "final_surprise": final,
        "final_complexity": 0.01 if chosen_order is not None else 0.0,
        "cv_curve": [_point(index + 1, value) for index, value in enumerate(values)],
    }


def _error(task: str) -> dict:
    return {
        "task": task,
        "status": "error",
        "error_type": "ValueError",
        "error": "synthetic bad task",
        "chosen_order": None,
        "ceiling_detected": False,
        "selected_reason": "error while diagnosing task",
        "final_surprise": None,
        "final_complexity": None,
        "cv_curve": [],
    }


def _report(tasks: list[dict]) -> dict:
    return {"summary": {"tasks": len(tasks)}, "tasks_detail": tasks}


def test_analyze_report_mixed_orders_is_healthy_adaptive() -> None:
    tasks = [
        _ok("order1_a", 1),
        _ok("order1_b", 1),
        _ok("order2_a", 2),
        _ok("order2_b", 2),
        _ok("ceiling", None, ceiling=True),
        _ok("order3", 3),
    ]

    analysis = analyze_report(_report(tasks))

    assert analysis["summary"]["regime"] == "healthy_adaptive"
    assert analysis["summary"]["order_counts"] == {"1": 2, "2": 2, "3": 1, "none": 1}
    assert analysis["summary"]["ceiling_rate"] == 1 / 6
    assert analysis["summary"]["mean_surprise_by_order"]["1"] == 0.7
    assert analysis["summary"]["mean_complexity_by_order"]["3"] == 0.03


def test_analyze_report_many_max_order_choices_is_over_climbing() -> None:
    tasks = [_ok(f"max_{index}", 3) for index in range(6)] + [_ok("low", 1)]

    analysis = analyze_report(_report(tasks))

    assert analysis["summary"]["regime"] == "over_climbing"
    assert analysis["summary"]["max_order_rate"] == 6 / 7


def test_analyze_report_many_ceilings_is_ceiling_dominated() -> None:
    tasks = [_ok(f"ceil_{index}", None, ceiling=True) for index in range(7)] + [_ok("order1", 1)]

    analysis = analyze_report(_report(tasks))

    assert analysis["summary"]["regime"] == "ceiling_dominated"
    assert analysis["summary"]["ceiling_rate"] == 7 / 8


def test_analyze_report_many_errors_is_too_many_errors() -> None:
    tasks = [_ok(f"ok_{index}", 1) for index in range(5)] + [_error("bad_a"), _error("bad_b")]

    analysis = analyze_report(_report(tasks))

    assert analysis["summary"]["regime"] == "too_many_errors"
    assert analysis["summary"]["errors"] == 2


def test_analyze_report_too_few_ok_tasks_is_insufficient_data() -> None:
    tasks = [_ok("ok_a", 1), _ok("ok_b", 2), _ok("ok_c", None, ceiling=True), _error("bad")]

    analysis = analyze_report(_report(tasks))

    assert analysis["summary"]["regime"] == "insufficient_data"


def test_interesting_tasks_returns_ceiling_max_order_and_error_examples() -> None:
    tasks = [
        _ok("plain", 1, values=(0.98, 0.97, 0.96)),
        _ok("ceiling", None, ceiling=True),
        _ok("max_order", 3),
        _error("bad"),
    ]

    selected = interesting_tasks(tasks, limit=10)
    by_task = {item["task"]: item for item in selected}

    assert by_task["ceiling"]["reason"] == "ceiling_detected"
    assert by_task["max_order"]["reason"] == "max_order_reached"
    assert by_task["bad"]["reason"] == "task_error"


def test_report_analysis_has_no_function_named_solve() -> None:
    source = Path("src/ontologic_core/report_analysis.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "solve" not in function_names


def test_report_analysis_src_avoids_score_lane_language() -> None:
    source = Path("src/ontologic_core/report_analysis.py").read_text(encoding="utf-8").lower()
    for forbidden in ["submission", "kaggle", "leaderboard", "oracle"]:
        assert forbidden not in source
