# M19: Self-Induced Factor Space

M18 showed that the hand-authored hierarchy did not reliably improve the Ontologic B-lane microscope. M19 therefore removes hand-authored semantic expansion from the new lane and asks the system to induce anonymous latent factors from raw cell experience.

ARC remains a microscope for observing structure growth. It is not the optimization target, and this work does not add task-family rules or output construction machinery.

## Fixed raw substrate

The induced path starts from only primitive per-cell observations:

- train-pair identity,
- input/output side indicator,
- normalized row and column coordinates,
- centered row and column coordinates,
- normalized color value,
- optional color one-hot coordinates,
- normalized cell index.

No higher-level descriptors are appended in induced mode.

## Anonymous candidate generation

`FactorInducer` creates unnamed candidate coordinates with generic numeric maps:

- random linear projections,
- products between primitive columns,
- sinusoidal random projections,
- thresholded sparse projections.

These candidates are not named as semantic operations. They are just latent coordinates.

## Survival criterion

Candidates survive only when they reduce leave-one-train-pair-out surprise after sparsity, complexity, and redundancy pressure. The selected matrix is returned as an `InducedFactorSpace` with diagnostics for candidate scores, redundancy, selected count, and compression gain.

## CLI use

The lab and sweep CLIs accept:

```bash
--factor-mode induced
--induced-candidates 256
--induced-survivors 32
--induced-seed 0
```

In induced mode, the lab reports induced metadata including selected factor count and mean compression gain. The sweep compact output carries the same induced metadata so runs can be compared without inspecting full per-task details.

## Ablation

`ablate_induced_factors.py` compares:

- basic baseline,
- induced runs across multiple seeds,
- candidate counts 64, 128, and 256,
- survivor counts 8, 16, and 32.

Useful induced behavior should appear across seeds, keep `healthy_adaptive` dominant, reduce ceiling rate or improve relative improvement, and avoid exploding max-order rate.
