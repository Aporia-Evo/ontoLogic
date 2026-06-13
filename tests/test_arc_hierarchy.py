from __future__ import annotations

import numpy as np

from ontologic_core.arc_hierarchy import analyze_scene, component_at_or_nearest


def _component_signature(scene):
    return [
        (component.component_id, component.color, component.area, component.bbox)
        for component in scene.components
    ]


def test_connected_components_are_deterministic() -> None:
    grid = [
        [0, 1, 1, 0],
        [0, 1, 0, 2],
        [3, 0, 2, 2],
    ]

    first = analyze_scene(grid)
    second = analyze_scene(grid)

    assert _component_signature(first) == _component_signature(second)
    assert first.labels.tolist() == second.labels.tolist()


def test_background_tie_break_is_deterministic() -> None:
    scene = analyze_scene([[0, 1], [1, 0]])

    assert scene.stats.background_color == 0
    assert scene.stats.color_counts[:2] == (2, 2)


def test_one_by_one_grid_works() -> None:
    scene = analyze_scene([[7]])

    assert scene.stats.height == 1
    assert scene.stats.width == 1
    assert scene.stats.background_color == 7
    assert scene.stats.component_count == 0
    assert scene.components == ()
    assert component_at_or_nearest(scene, 0, 0) is None


def test_component_stats_are_finite() -> None:
    scene = analyze_scene(
        [
            [0, 0, 0, 0, 0],
            [0, 4, 4, 4, 0],
            [0, 4, 0, 4, 0],
            [0, 4, 4, 4, 0],
            [0, 0, 0, 0, 0],
        ]
    )

    component = scene.components[0]
    values = np.asarray(
        [
            component.area,
            *component.bbox,
            component.centroid_r,
            component.centroid_c,
            component.bbox_height,
            component.bbox_width,
            component.normalized_area,
            component.normalized_bbox_size,
            *component.relative_centroid,
            component.simple_hole_count,
            scene.stats.foreground_density,
        ],
        dtype=np.float64,
    )
    assert np.isfinite(values).all()
    assert component.simple_hole_count == 1


def test_nearest_component_is_deterministic() -> None:
    scene = analyze_scene(
        [
            [1, 0, 2],
            [0, 0, 0],
            [0, 0, 0],
        ]
    )

    first = component_at_or_nearest(scene, 1, 1)
    second = component_at_or_nearest(scene, 1, 1)

    assert first is not None
    assert second is not None
    assert first.component_id == second.component_id == 0


def test_no_output_grid_is_used() -> None:
    input_grid = [[0, 1], [0, 0]]

    first = analyze_scene(input_grid)
    second = analyze_scene(input_grid)

    assert _component_signature(first) == _component_signature(second)
