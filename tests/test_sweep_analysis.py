from __future__ import annotations

import ast
from pathlib import Path

import numpy as np

from ontologic_core.adaptive_order_gate import (
    _fit_ridge_dual_with_bias,
    _fit_ridge_primal_with_bias,
    _mse,
)
from ontologic_core.sweep_analysis import build_sweep_report, compact_run, summarize_sweep


def _run(regime: str, lambda_value: float = 1.0, margin: float = 0.02) -> dict:
    return {
        "lambda": lambda_value,
        "margin": margin,
        "regime": regime,
        "order_counts": {"1": 2, "2": 2, "3": 1, "none": 1},
        "ceiling_rate": 0.15,
        "max_order_rate": 0.10,
        "mean_final_surprise": 0.4,
        "mean_relative_improvement": 0.3,
    }


def test_synthetic_sweep_same_regime_is_stable() -> None:
    runs = [_run("healthy_adaptive", lambda_value=value) for value in (0.1, 1.0, 10.0)]

    summary = summarize_sweep(runs)

    assert summary["stable_regime"] is True
    assert summary["dominant_regime"] == "healthy_adaptive"
    assert summary["regime_counts"] == {"healthy_adaptive": 3}
    assert any("most settings" in note for note in summary["notes"])


def test_synthetic_sweep_mixed_extremes_is_unstable() -> None:
    runs = [
        _run("healthy_adaptive", lambda_value=0.1, margin=0.02),
        _run("over_climbing", lambda_value=1.0, margin=0.005),
        _run("ceiling_dominated", lambda_value=10.0, margin=0.05),
    ]

    report = build_sweep_report(runs)

    assert report["summary"]["stable_regime"] is False
    assert report["summary"]["regime_counts"] == {
        "ceiling_dominated": 1,
        "healthy_adaptive": 1,
        "over_climbing": 1,
    }
    assert any("over_climbing and ceiling_dominated" in note for note in report["summary"]["notes"])


def test_synthetic_sweep_single_healthy_setting_is_fragile() -> None:
    runs = [_run("healthy_adaptive"), _run("under_climbing"), _run("under_climbing")]

    summary = summarize_sweep(runs)

    assert summary["stable_regime"] is False
    assert any("fragile" in note for note in summary["notes"])


def test_compact_run_keeps_required_fields() -> None:
    analysis = {
        "summary": {
            "regime": "healthy_adaptive",
            "order_counts": {"1": 4, "2": 3, "3": 1, "none": 2},
            "ceiling_rate": 0.2,
            "max_order_rate": 0.1,
            "mean_final_surprise": 0.42,
            "mean_relative_improvement": 0.34,
        }
    }

    compact = compact_run(1.0, 0.02, analysis)

    assert compact == {
        "lambda": 1.0,
        "margin": 0.02,
        "regime": "healthy_adaptive",
        "order_counts": {"1": 4, "2": 3, "3": 1, "none": 2},
        "ceiling_rate": 0.2,
        "max_order_rate": 0.1,
        "mean_final_surprise": 0.42,
        "mean_relative_improvement": 0.34,
    }


def test_sweep_analysis_has_no_forbidden_growth_api_name() -> None:
    source = Path("src/ontologic_core/sweep_analysis.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    forbidden_name = "so" + "lve"
    assert forbidden_name not in function_names


def test_sweep_analysis_src_avoids_score_lane_language() -> None:
    source = Path("src/ontologic_core/sweep_analysis.py").read_text(encoding="utf-8").lower()
    forbidden_terms = ["kag" + "gle", "sub" + "mission", "or" + "acle", "leader" + "board"]
    for forbidden in forbidden_terms:
        assert forbidden not in source


def test_ridge_primal_and_sample_space_paths_match_held_out_surprise() -> None:
    rng = np.random.default_rng(123)
    train_x = np.column_stack([np.ones(5), rng.normal(size=(5, 9))])
    true_weights = rng.normal(size=(10, 2))
    train_y = train_x @ true_weights + rng.normal(scale=0.01, size=(5, 2))
    held_x = np.column_stack([np.ones(3), rng.normal(size=(3, 9))])
    held_y = held_x @ true_weights + rng.normal(scale=0.01, size=(3, 2))

    primal_weights = _fit_ridge_primal_with_bias(train_x, train_y, lambda_=0.7)
    dual_weights = _fit_ridge_dual_with_bias(train_x, train_y, lambda_=0.7)

    primal_surprise = _mse(held_y, held_x @ primal_weights)
    dual_surprise = _mse(held_y, held_x @ dual_weights)

    assert np.isclose(primal_surprise, dual_surprise, rtol=1e-10, atol=1e-10)
