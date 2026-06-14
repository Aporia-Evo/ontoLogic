# Ontologic Milestone Log

This log preserves the research trajectory of the clean Ontologic B-lane.

The repository boundary is:

```text
ARC is not the goal. ARC is the microscope.
```

## M16 — ARC as ontology microscope

Goal: build a minimal diagnostic environment where a gate grows structure from train-pair experience.

Implemented components:

- `AdaptiveOrderGate.grow_structure`,
- generic train-pair factor extraction,
- leave-one-out surprise evaluation,
- complexity pressure,
- least-sufficient-order selection,
- ceiling detection,
- diagnostic JSON reports.

Main acceptance conditions:

- order-1 synthetic world chooses order 1,
- order-2 synthetic world climbs to order 2,
- underdetermined/simple worlds do not blindly climb,
- test outputs do not influence selection,
- no score-lane imports.

Observed ARC-50 diagnostic result:

```text
order_counts: {1: 27, 2: 9, 3: 1, none: 13}
ceiling_rate: 0.26
max_order_rate: 0.02
mean_final_surprise: 3.4504
mean_relative_improvement: 0.3466
regime: healthy_adaptive
```

Interpretation:

The gate behaved conservatively. It usually preferred simple structure, climbed sometimes, rarely hit max order, and honestly returned ceilings on underdetermined tasks.

## M16d — report analysis

Added post-hoc analyzer for ontology lab JSON reports.

Regime labels:

- `healthy_adaptive`,
- `over_climbing`,
- `under_climbing`,
- `ceiling_dominated`,
- `too_many_errors`,
- `insufficient_data`.

The analyzer is an interpretability layer. It does not alter feature extraction, gate behavior, or output construction.

## M16f — parameter stability sweep

Goal: verify that healthy behavior is not a one-setting accident.

Observed ARC-50 sweep:

```text
runs: 9
regime_counts: {healthy_adaptive: 9}
stable_regime: true
mean_ceiling_rate: ~0.256
mean_max_order_rate: ~0.033
mean_relative_improvement: ~0.341
```

Interpretation:

The adaptive-order gate appeared stable across nearby lambda/margin settings.

## M17 — hierarchical factors

Goal: test whether richer perception improves the gate.

Added optional `hierarchical` factor mode with:

- scene statistics,
- connected components,
- component geometry,
- component rank,
- component color,
- bounding-box relations,
- centroid relations,
- global geometry,
- local density,
- hole/enclosure signals.

Result:

The hierarchy was stable in controlled order-2 comparisons but was not clearly beneficial. Full hierarchy increased feature width and tended to hurt or dilute the basic signal.

Interpretation:

Richer human-authored perception is not automatically better. It can become noise or implicit feature engineering.

## M18 — factor-group ablation

Goal: isolate which pieces of M17 helped or hurt.

Result summary:

```text
baseline: basic
helps: only basic + component_color, tiny effect
hurts: many standalone or broad hierarchy groups
full_hierarchical: worse than basic
unstable: several isolated semantic groups
```

Important numeric readout from the ARC-50 order-2 group ablation:

```text
basic:
  mean_ceiling_rate: 0.2556
  mean_max_order_rate: 0.2222
  mean_relative_improvement: 0.3384

full_hierarchical:
  mean_ceiling_rate: 0.3067
  mean_relative_improvement: 0.3233

basic + component_color:
  delta_ceiling_rate_vs_basic: -0.0111
  delta_relative_improvement_vs_basic: +0.0005
```

Interpretation:

M18 was useful as a diagnostic audit, but it also showed that manually named factor groups should not become the final ontology mechanism.

## Conceptual pivot after M18

The project rule became stricter:

```text
Objects, groups, and rules must not be inputs.
They may only be post-hoc interpretations of survived latent factors.
```

This rules out a final design based on hand-authored component semantics, handcrafted deltas, or ARC transformation names.

## M19 — self-induced factor space

Goal: replace hand-authored semantic expansion with anonymous factor induction from primitive raw substrate.

Fixed raw substrate:

- pair identity,
- input/output side,
- normalized row/column,
- centered row/column,
- normalized color,
- optional color one-hot primitives,
- normalized cell index.

Candidate factor families:

- sparse random projections,
- primitive feature products,
- sinusoidal projections,
- thresholded projections.

Survival rule:

Candidates survive only if they reduce train-only surprise under complexity, redundancy, and stability pressure.

## M19 evolution runner

Goal: evolve factor-induction parameters using ontology diagnostics only.

Parameters include:

- induced candidate count,
- survivor count,
- projection sparsity,
- interaction fraction,
- threshold fraction,
- Fourier fraction,
- max feature width,
- complexity weight,
- redundancy weight,
- stability weight,
- induced seed.

Fitness uses diagnostic behavior only, not ARC exact-match score.

First evolution status:

```text
engine: works
fitness: improves across generations
best_fitness observed: about -0.1402
reported stable: false
known issue: insufficient_data slices contaminate aggregate means
```

Next required fix:

- split raw metrics from valid-slice metrics,
- do not average insufficient-data slices as zero-valued valid runs,
- penalize invalid slices separately,
- rank finalists by valid metrics plus invalid-slice penalty.

## Current research thesis

The repeated pattern is:

```text
Core gate/memory mechanism can be healthy.
The bottleneck moves to perception / factor induction / binding.
```

For ARC, the bottleneck is factor induction.
For PDMemory/RAG experiments, the analogous bottleneck is entity/state binding.

The next scientific step is not to add a solver. It is to improve self-induced perception while preserving the B-lane boundary.
