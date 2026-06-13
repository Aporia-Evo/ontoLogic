from __future__ import annotations

from pathlib import Path


def test_src_avoids_score_lane_and_answer_construction_language() -> None:
    forbidden_terms = [
        "so" + "lve",
        "pre" + "dict",
        "sub" + "mission",
        "or" + "acle",
        "leader" + "board",
        "kag" + "gle",
    ]
    for path in Path("src").rglob("*.py"):
        source = path.read_text(encoding="utf-8").lower()
        for forbidden in forbidden_terms:
            assert forbidden not in source, f"{forbidden!r} found in {path}"
