from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

from plot_m19_diagnostics import (  # noqa: E402
    load_json,
    plot_ablation_deltas,
    plot_evolution_behavior,
    plot_evolution_fitness,
    plot_regime_counts,
)


def _evolution_report():
    return {
        "generations": [
            {
                "generation": 0,
                "best_fitness": 0.1,
                "mean_fitness": 0.05,
                "mean_relative_improvement": 0.02,
                "mean_ceiling_rate": 0.4,
                "mean_max_order_rate": 0.1,
            },
            {
                "generation": 1,
                "best_fitness": 0.2,
                "mean_fitness": 0.08,
                "mean_relative_improvement": 0.04,
                "mean_ceiling_rate": 0.3,
                "mean_max_order_rate": 0.12,
            },
        ],
        "finalists": [
            {"genome_id": "alpha", "fitness": 0.2, "mean_selected_factor_count": 8},
            {"genome_id": "beta", "fitness": 0.15, "mean_selected_factor_count": 12},
        ],
    }


def _ablation_report():
    return {
        "summary": {"regime_counts": {"healthy_adaptive": 2, "under_climbing": 1}},
        "runs": [
            {
                "label": "basic",
                "factor_mode": "basic",
                "mean_relative_improvement": 0.10,
                "ceiling_rate": 0.50,
                "max_order_rate": 0.10,
                "regime": "under_climbing",
            },
            {
                "label": "seed_0",
                "factor_mode": "induced",
                "induced_seed": 0,
                "mean_relative_improvement": 0.15,
                "ceiling_rate": 0.40,
                "max_order_rate": 0.11,
                "regime": "healthy_adaptive",
            },
            {
                "label": "seed_1",
                "factor_mode": "induced",
                "induced_seed": 1,
                "mean_relative_improvement": 0.13,
                "ceiling_rate": 0.45,
                "max_order_rate": 0.12,
                "regime": "healthy_adaptive",
            },
        ],
    }


def test_evolution_fitness_plot_is_created(tmp_path):
    paths = plot_evolution_fitness(_evolution_report(), tmp_path / "plots")
    assert [path.name for path in paths] == ["evolution_fitness.png"]
    assert paths[0].exists()


def test_ablation_deltas_plot_is_created(tmp_path):
    paths = plot_ablation_deltas(_ablation_report(), tmp_path / "plots")
    assert [path.name for path in paths] == ["ablation_deltas.png"]
    assert paths[0].exists()


def test_missing_optional_fields_do_not_crash(tmp_path):
    assert plot_evolution_behavior({"generations": [{"generation": 0}]}, tmp_path) == []
    assert plot_regime_counts({"runs": []}, tmp_path) == []


def test_output_directory_is_created_automatically(tmp_path):
    out_dir = tmp_path / "nested" / "plots"
    assert not out_dir.exists()
    paths = plot_evolution_fitness(_evolution_report(), out_dir)
    assert out_dir.exists()
    assert paths[0].exists()


def test_svg_option_creates_svg_files(tmp_path):
    paths = plot_evolution_fitness(_evolution_report(), tmp_path, svg=True)
    assert {path.suffix for path in paths} == {".png", ".svg"}
    assert all(path.exists() for path in paths)


def test_no_arc_output_grids_are_plotted():
    text = Path("plot_m19_diagnostics.py").read_text(encoding="utf-8")
    forbidden_calls = ["imshow", "matshow", "pcolor", "pcolormesh"]
    assert [call for call in forbidden_calls if call in text] == []


def test_no_forbidden_language_in_plotting_source():
    text = Path("plot_m19_diagnostics.py").read_text(encoding="utf-8").lower()
    forbidden = ["solve", "predict", "submission", "oracle", "leaderboard", "kaggle"]
    assert [word for word in forbidden if word in text] == []


def test_load_json(tmp_path):
    path = tmp_path / "report.json"
    path.write_text('{"runs": []}', encoding="utf-8")
    assert load_json(path) == {"runs": []}
