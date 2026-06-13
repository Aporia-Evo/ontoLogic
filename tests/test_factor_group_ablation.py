from __future__ import annotations

from ablate_factor_groups import build_ablation_item, summarize_ablation_report


def _sweep(regime: str, ceiling: float, max_order: float, improvement: float) -> dict:
    return {
        "summary": {"dominant_regime": regime, "regime_counts": {regime: 1}},
        "runs": [
            {
                "ceiling_rate": ceiling,
                "max_order_rate": max_order,
                "mean_relative_improvement": improvement,
            }
        ],
    }


def test_ablation_report_computes_deltas_and_helpful_verdict() -> None:
    baseline = summarize_ablation_report(_sweep("healthy_adaptive", 0.30, 0.02, 0.25))
    item = build_ablation_item(
        "basic+component_geometry",
        "hierarchical",
        ["basic", "component_geometry"],
        _sweep("healthy_adaptive", 0.20, 0.03, 0.31),
        baseline,
    )

    assert item["delta_ceiling_rate_vs_basic"] == -0.09999999999999998
    assert item["delta_relative_improvement_vs_basic"] == 0.06
    assert item["verdict"] == "helps"


def test_ablation_report_marks_hurts_and_unstable() -> None:
    baseline = summarize_ablation_report(_sweep("healthy_adaptive", 0.30, 0.02, 0.25))
    hurts = build_ablation_item(
        "component_color",
        "hierarchical",
        ["component_color"],
        _sweep("healthy_adaptive", 0.36, 0.02, 0.20),
        baseline,
    )
    unstable = build_ablation_item(
        "full_hierarchical",
        "hierarchical",
        ["basic", "scene_stats"],
        _sweep("over_climbing", 0.20, 0.70, 0.40),
        baseline,
    )

    assert hurts["verdict"] == "hurts"
    assert unstable["verdict"] == "unstable"
