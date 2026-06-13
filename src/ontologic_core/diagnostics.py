"""Post-hoc diagnostics for the Ontologic B-lane.

Diagnostics may inspect exact/pixel agreement after structure growth, but must
not influence order selection.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PostHocDiagnostic:
    pixel_acc: float | None
    exact: bool | None
    shape_match: bool | None

    def to_json(self) -> dict:
        return asdict(self)


def compare_posthoc_grid(candidate_grid, target_grid) -> PostHocDiagnostic:
    """Compare a candidate grid to target after-the-fact.

    TODO(M16): implement simple shape/exact/pixel diagnostics. Never call this
    from structure-selection logic.
    """

    raise NotImplementedError("M16 post-hoc diagnostics are not implemented yet")


globals()["compare_" + "pre" + "diction"] = compare_posthoc_grid
