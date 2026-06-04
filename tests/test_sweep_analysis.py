from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np

from ontologic_core.adaptive_order_gate import ridge_predict, ridge_primal_predict, ridge_sample_space_predict
from ontologic_core.sweep_analysis import build_run_record, build_sweep_report, summarize_sweep


def _analysis(regime: str, *, order_counts: dict[str, int] | None = None) -> dict:
    return {
        "summary": {
            "regime": regime,
            "order_counts": order_counts or {"1": 2, "2": 2, "3": 1, "none": 1},
            "ceiling_rate": 0.2,
            "max_order_rate": 0.1,
            "mean_final_surprise": 0.42,
            "mean_relative_improvement": 0.34,
        }
    }


def _run(regime: str, index: int) -> dict:
    return build_run_record(0.1 + index, 0.02, _analysis(regime))


def test_synthetic_sweep_same_regime_is_stable() -> None:
    runs = [_run("healthy_adaptive", index) for index in range(6)]

    report = build_sweep_report(runs)

    assert report["summary"]["stable_regime"] is True
    assert report["summary"]["dominant_regime"] == "healthy_adaptive"
    assert report["summary"]["regime_counts"] == {"healthy_adaptive": 6}
    assert report["runs"][0]["mean_relative_improvement"] == 0.34


def test_synthetic_sweep_mixed_extremes_is_not_stable() -> None:
    runs = [
        _run("healthy_adaptive", 0),
        _run("over_climbing", 1),
        _run("ceiling_dominated", 2),
        _run("under_climbing", 3),
    ]

    summary = summarize_sweep(runs)

    assert summary["stable_regime"] is False
    assert "rows include both over_climbing and ceiling_dominated regimes" in summary["notes"]


def test_synthetic_sweep_single_healthy_row_is_fragile_not_stable() -> None:
    runs = [_run("healthy_adaptive", 0), _run("under_climbing", 1), _run("under_climbing", 2)]

    summary = summarize_sweep(runs)

    assert summary["stable_regime"] is False
    assert "healthy_adaptive appears in only one row" in summary["notes"]


def test_sweep_src_avoids_score_lane_language() -> None:
    source = Path("src/ontologic_core/sweep_analysis.py").read_text(encoding="utf-8").lower()
    for forbidden in ["submission", "kaggle", "leaderboard", "oracle", "solver"]:
        assert forbidden not in source


def test_sweep_public_names_use_microscope_language() -> None:
    import ontologic_core.sweep_analysis as sweep_analysis

    for name, value in vars(sweep_analysis).items():
        if inspect.isfunction(value):
            assert "solve" not in name.lower()


def test_sample_space_ridge_matches_primal_on_small_held_rows() -> None:
    rng = np.random.default_rng(17)
    raw_x = rng.normal(size=(5, 8))
    train_x = np.hstack([np.ones((raw_x.shape[0], 1)), raw_x])
    held_raw = rng.normal(size=(3, 8))
    held_x = np.hstack([np.ones((held_raw.shape[0], 1)), held_raw])
    true_weights = rng.normal(size=(train_x.shape[1], 2))
    train_y = train_x @ true_weights + rng.normal(scale=0.01, size=(train_x.shape[0], 2))
    held_y = held_x @ true_weights

    lambda_ = 0.7
    primal = ridge_primal_predict(train_x, train_y, held_x, lambda_)
    sample_space = ridge_sample_space_predict(train_x, train_y, held_x, lambda_)
    memory_safe = ridge_predict(train_x, train_y, held_x, lambda_)

    assert np.allclose(sample_space, primal, atol=1e-10)
    assert np.allclose(memory_safe, primal, atol=1e-10)
    primal_surprise = float(np.mean((held_y - primal) ** 2))
    sample_space_surprise = float(np.mean((held_y - sample_space) ** 2))
    assert np.isclose(sample_space_surprise, primal_surprise, atol=1e-12)
