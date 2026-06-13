from __future__ import annotations

import json
from pathlib import Path

import pytest

import evolve_factor_induction as evolve


def _write_task(path: Path, offset: int) -> None:
    path.write_text(
        json.dumps(
            {
                "train": [
                    {"input": [[offset % 3, 1], [2, 3]], "output": [[1, 2], [3, 4]]},
                    {"input": [[1, offset % 4], [3, 2]], "output": [[2, 3], [4, 5]]},
                ],
                "test": [{"input": [[0, 1], [1, 0]]}],
            }
        ),
        encoding="utf-8",
    )


def test_tiny_evolution_run_writes_expected_shape(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    for idx in range(3):
        _write_task(data / f"task_{idx}.json", idx)
    out = tmp_path / "evolved.json"

    evolve.main(
        [
            "--data",
            str(data),
            "--limit",
            "3",
            "--generations",
            "1",
            "--population",
            "3",
            "--elite-count",
            "1",
            "--max-order",
            "2",
            "--slice-mode",
            "all",
            "--lambdas",
            "1.0",
            "--margins",
            "0.02",
            "--json-out",
            str(out),
        ]
    )

    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert set(loaded) == {"summary", "generations", "finalists"}
    assert len(loaded["generations"]) == 1
    assert loaded["summary"]["generations"] == 1
    assert loaded["summary"]["population"] == 3
    assert loaded["finalists"]
    assert set(evolve.GENOME_FIELDS) <= set(loaded["summary"]["best_genome"])


def test_missing_data_path_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        evolve.run_evolution(
            tmp_path / "missing",
            limit=None,
            generations=1,
            population=3,
            max_order=2,
            seed=0,
            elite_count=1,
            slice_mode="all",
            lambdas=[1.0],
            margins=[0.02],
        )


def test_evolution_source_avoids_forbidden_terms() -> None:
    source = Path(evolve.__file__).read_text(encoding="utf-8")
    forbidden = ["solve", "predict", "submission", "leaderboard", "oracle", "Kaggle"]
    for term in forbidden:
        assert term not in source
