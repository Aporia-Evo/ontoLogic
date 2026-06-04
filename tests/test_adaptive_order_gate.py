from __future__ import annotations

import ast
import inspect
from pathlib import Path

import numpy as np

from ontologic_core.adaptive_order_gate import AdaptiveOrderGate, expand_features
from ontologic_core.arc_factors import PairExperience


FORBIDDEN_NAMES = {"solve", "submission", "leaderboard", "oracle"}
SCORE_LANE_MODULES = {
    "arc_union_orchestrator",
    "arc_evo_operator_lab",
    "arc_candidate_oracle",
}


def _pair(features: np.ndarray, targets: np.ndarray) -> PairExperience:
    return PairExperience(
        features=np.asarray(features, dtype=np.float64),
        targets=np.asarray(targets, dtype=np.float64),
        output_shape=(1, 1),
    )


def _sampled_pairs(seed: int, coefficient: np.ndarray, rows_per_pair: int = 10) -> list[PairExperience]:
    rng = np.random.default_rng(seed)
    pairs = []
    for _ in range(8):
        x = rng.uniform(-2.0, 2.0, size=(rows_per_pair, 2))
        y = expand_features(x, 2) @ coefficient
        pairs.append(_pair(x, y))
    return pairs


def test_synthetic_order_1_world_chooses_order_1() -> None:
    coefficient = np.array([0.3, 1.7, -0.8, 0.0, 0.0, 0.0])
    gate = AdaptiveOrderGate(max_order=3, lambda_=1e-6, margin=0.01)

    diagnosis = gate.grow_structure(_sampled_pairs(seed=11, coefficient=coefficient))

    assert diagnosis.chosen_order == 1
    assert not diagnosis.ceiling_detected
    assert diagnosis.cv_curve[0].surprise < diagnosis.cv_curve[0].baseline_surprise


def test_synthetic_order_2_world_climbs_to_order_2() -> None:
    coefficient = np.array([0.2, 0.1, -0.2, 0.0, 2.5, 0.0])
    gate = AdaptiveOrderGate(max_order=3, lambda_=1e-6, margin=0.01)

    diagnosis = gate.grow_structure(_sampled_pairs(seed=23, coefficient=coefficient))

    assert diagnosis.chosen_order == 2
    assert not diagnosis.ceiling_detected
    order_1, order_2 = diagnosis.cv_curve[0], diagnosis.cv_curve[1]
    assert order_2.score < order_1.score - gate.margin


def test_underdetermined_parity_like_world_does_not_blindly_climb_to_max_order() -> None:
    pairs = [
        _pair([[0.0, 0.0]], [0.0]),
        _pair([[0.0, 1.0]], [1.0]),
        _pair([[1.0, 0.0]], [1.0]),
    ]
    gate = AdaptiveOrderGate(max_order=3, lambda_=0.25, margin=0.02)

    diagnosis = gate.grow_structure(pairs)

    assert diagnosis.ceiling_detected or diagnosis.chosen_order < 3


def test_no_forbidden_public_function_names() -> None:
    import ontologic_core.adaptive_order_gate as gate_module

    for name, value in vars(gate_module).items():
        if inspect.isfunction(value):
            assert name.lower() not in FORBIDDEN_NAMES
        if inspect.isclass(value):
            for method_name, method_value in vars(value).items():
                if inspect.isfunction(method_value):
                    assert method_name.lower() not in FORBIDDEN_NAMES


def test_no_imports_from_score_lane_modules() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    python_files = [*repo_root.joinpath("src").rglob("*.py"), *repo_root.joinpath("tests").rglob("*.py")]

    for path in python_files:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                assert imported.isdisjoint(SCORE_LANE_MODULES), path
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                assert node.module.split(".")[0] not in SCORE_LANE_MODULES, path
