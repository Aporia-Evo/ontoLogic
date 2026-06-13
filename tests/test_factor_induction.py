from pathlib import Path

import numpy as np

from ontologic_core.arc_factors import extract_task_experience
from ontologic_core.factor_induction import FactorInducer, extract_raw_observations


def _task():
    return {
        "train": [
            {"input": [[0, 1], [2, 3]], "output": [[1, 2], [3, 4]]},
            {"input": [[3, 2], [1, 0]], "output": [[4, 3], [2, 1]]},
        ]
    }


def test_raw_observations_are_primitive_width():
    raw = extract_raw_observations(_task())
    assert raw.shape == (8, 18)
    assert np.isfinite(raw).all()
    assert set(np.unique(raw[:, 1])) == {1.0}


def test_induced_factors_deterministic_for_fixed_seed():
    raw = extract_raw_observations(_task())
    targets = np.array([1, 2, 3, 4, 4, 3, 2, 1])
    groups = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    a = FactorInducer(n_candidates=32, n_survivors=4, seed=7).induce(raw, targets, groups)
    b = FactorInducer(n_candidates=32, n_survivors=4, seed=7).induce(raw, targets, groups)
    assert a.selected_candidate_indices == b.selected_candidate_indices
    np.testing.assert_allclose(a.features, b.features)


def test_induced_factors_different_seed_does_not_crash():
    raw = extract_raw_observations(_task())
    targets = np.array([1, 2, 3, 4, 4, 3, 2, 1])
    groups = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    space = FactorInducer(n_candidates=32, n_survivors=4, seed=13).induce(raw, targets, groups)
    assert space.features.shape[0] == raw.shape[0]
    assert space.feature_width <= 4


def test_no_forbidden_terms_in_factor_induction_source():
    text = Path("src/ontologic_core/factor_induction.py").read_text(encoding="utf-8").lower()
    forbidden = [
        "object",
        "component",
        "connected component",
        "shape",
        "bbox",
        "centroid",
        "hole",
        "mirror",
        "rotate",
        "copy",
        "crop",
        "fill",
        "recolor",
        "line",
        "symmetry",
        "pattern",
        "histogram",
        "density",
        "entropy",
        "delta",
        "solve",
        "predict",
        "submission",
        "oracle",
        "leaderboard",
        "kaggle",
    ]
    assert [word for word in forbidden if word in text] == []


def test_induced_mode_keeps_rows_and_targets_aligned():
    pairs = extract_task_experience(
        _task(),
        mode="induced",
        induced_candidates=32,
        induced_survivors=4,
        induced_seed=0,
    )
    assert len(pairs) == 2
    for pair in pairs:
        assert pair.features.shape[0] == pair.targets.shape[0]
        assert pair.features.shape[1] <= 4
