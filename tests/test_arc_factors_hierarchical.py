from __future__ import annotations

import numpy as np
import pytest

from ontologic_core.arc_factors import extract_pair_experience, extract_task_experience


def test_hierarchical_mode_keeps_rows_and_targets() -> None:
    input_grid = [[0, 1, 0], [2, 2, 0]]
    output_grid = [[1, 0], [2, 2]]

    basic = extract_pair_experience(input_grid, output_grid, mode="basic")
    hierarchical = extract_pair_experience(input_grid, output_grid, mode="hierarchical")

    assert hierarchical.features.shape[0] == basic.features.shape[0]
    assert hierarchical.output_shape == basic.output_shape
    assert hierarchical.targets.tolist() == basic.targets.tolist()


def test_hierarchical_feature_width_exceeds_basic_width() -> None:
    input_grid = [[0, 1], [2, 0]]
    output_grid = [[1, 2], [0, 0]]

    basic = extract_pair_experience(input_grid, output_grid)
    hierarchical = extract_pair_experience(input_grid, output_grid, mode="hierarchical")

    assert hierarchical.features.shape[1] > basic.features.shape[1]


def test_hierarchical_features_are_finite() -> None:
    experience = extract_pair_experience(
        [[0, 0, 0], [0, 3, 0], [2, 0, 2]],
        [[3, 0, 3], [0, 2, 0]],
        mode="hierarchical",
    )

    assert np.isfinite(experience.features).all()


def test_changing_test_section_does_not_change_extracted_experience() -> None:
    task = {
        "train": [{"input": [[0, 1], [0, 0]], "output": [[1, 0], [0, 1]]}],
        "test": [{"input": [[9]], "output": [[9]]}],
    }
    changed = {
        **task,
        "test": [{"input": [[8, 8]], "output": "not inspected"}],
    }

    first = extract_task_experience(task, mode="hierarchical")
    second = extract_task_experience(changed, mode="hierarchical")

    assert len(first) == len(second) == 1
    assert np.array_equal(first[0].features, second[0].features)
    assert np.array_equal(first[0].targets, second[0].targets)



def test_factor_group_selection_changes_width_deterministically() -> None:
    input_grid = [[0, 1], [2, 0]]
    output_grid = [[1, 2], [0, 0]]

    geometry_first = extract_pair_experience(
        input_grid, output_grid, mode="hierarchical", factor_groups=["component_geometry"]
    )
    geometry_second = extract_pair_experience(
        input_grid, output_grid, mode="hierarchical", factor_groups=["component_geometry"]
    )
    with_basic = extract_pair_experience(
        input_grid, output_grid, mode="hierarchical", factor_groups=["basic", "component_geometry"]
    )

    assert geometry_first.features.shape[1] == geometry_second.features.shape[1] == 4
    assert with_basic.features.shape[1] == 54
    assert np.array_equal(geometry_first.features, geometry_second.features)


def test_basic_mode_remains_unchanged_with_basic_group() -> None:
    input_grid = [[0, 1], [2, 0]]
    output_grid = [[1, 2], [0, 0]]

    default = extract_pair_experience(input_grid, output_grid)
    explicit = extract_pair_experience(input_grid, output_grid, mode="basic", factor_groups=["basic"])

    assert np.array_equal(default.features, explicit.features)
    assert np.array_equal(default.targets, explicit.targets)


def test_invalid_factor_group_raises_value_error() -> None:
    with pytest.raises(ValueError):
        extract_pair_experience([[0]], [[0]], mode="hierarchical", factor_groups=["not_a_group"])


def test_invalid_mode_raises_value_error() -> None:
    with pytest.raises(ValueError):
        extract_pair_experience([[0]], [[0]], mode="richer")
