from __future__ import annotations

import inspect


def test_adaptive_order_gate_has_no_score_lane_language() -> None:
    import ontologic_core.adaptive_order_gate as gate

    source = inspect.getsource(gate).lower()
    assert "arc_union_orchestrator" not in source
    assert "kaggle" not in source
    assert "submission" not in source
    assert "leaderboard" not in source


def test_public_api_is_structure_growth_language() -> None:
    import ontologic_core.adaptive_order_gate as gate

    assert hasattr(gate.AdaptiveOrderGate, "grow_structure")
    assert not hasattr(gate.AdaptiveOrderGate, "solve")
