from __future__ import annotations

import inspect

import numpy as np

from ontologic_core import arc_factors
from ontologic_core.arc_factors import extract_pair_experience, extract_task_experience


def test_extract_pair_experience_same_shape_rows_targets_and_finite() -> None:
    input_grid = [
        [0, 1, 1],
        [0, 1, 2],
    ]
    output_grid = [
        [1, 1, 0],
        [2, 2, 0],
    ]

    experience = extract_pair_experience(input_grid, output_grid)

    assert experience.output_shape == (2, 3)
    assert experience.features.shape[0] == np.asarray(output_grid).size
    assert len(experience.targets) == np.asarray(output_grid).size
    assert experience.targets.tolist() == [1, 1, 0, 2, 2, 0]
    assert experience.features.shape[1] > 0
    assert np.isfinite(experience.features).all()


def test_extract_pair_experience_different_shape_rows_targets_and_finite() -> None:
    input_grid = [
        [0, 1],
        [2, 2],
    ]
    output_grid = [
        [0, 1, 1, 1],
        [2, 2, 1, 1],
        [2, 2, 0, 0],
    ]

    experience = extract_pair_experience(input_grid, output_grid)

    assert experience.output_shape == (3, 4)
    assert experience.features.shape[0] == np.asarray(output_grid).size
    assert len(experience.targets) == np.asarray(output_grid).size
    assert np.isfinite(experience.features).all()


def test_extract_task_experience_ignores_test_section() -> None:
    task = {
        "train": [
            {
                "input": [[0, 1], [1, 0]],
                "output": [[1, 0], [0, 1]],
            }
        ],
        "test": [
            {
                "input": [[0]],
                "output": "would fail if inspected",
            }
        ],
    }

    experiences = extract_task_experience(task)

    assert len(experiences) == 1
    assert experiences[0].features.shape[0] == 4


def test_arc_factors_has_no_solve_api_or_score_lane_language() -> None:
    source = inspect.getsource(arc_factors).lower()

    assert not hasattr(arc_factors, "solve")
    assert "def solve" not in source
    assert "arc_union_orchestrator" not in source
    assert "arc_evo_operator_lab" not in source
    assert "arc_candidate_oracle" not in source
    assert "kaggle" not in source
    assert "submission" not in source
