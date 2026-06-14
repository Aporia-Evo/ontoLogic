# Ontologic Research Charter

This file is the canonical research note for the `ontoLogic` repository. It exists so the project does not collapse into a normal benchmark repository or lose the original conceptual thread while implementation work moves quickly.

The short version is deliberately simple:

```text
ARC is not the goal.
ARC is the microscope.
```

`ontoLogic` is the clean B-lane for testing whether a system can grow internal structure from experience. The benchmark-like environment is only a controlled world where structure growth, compression, underdetermination, and overfitting can be observed.

## Core question

The project is not asking:

```text
How many ARC tasks can this solve?
```

It asks:

```text
Can a self-calibrating mechanism grow the least sufficient internal structure from sparse experience, stop before overfitting, and honestly detect when the examples underdetermine the rule?
```

That distinction is the repository boundary.

## Scientific stance

Ontologic is about structure formation, not hand-written symbolic task solving.

The mechanism should be judged by whether it can:

1. absorb train-pair experience,
2. compress that experience into latent structure,
3. increase interaction order only when the evidence justifies it,
4. resist overfitting when sparse examples are ambiguous,
5. expose ceilings instead of pretending certainty,
6. separate perception/factor induction from output-score hacking.

Exact-match results can be useful as a post-hoc microscope, but they are not the objective and must not become the training pressure.

## B-lane boundary

Allowed:

- train pairs as experience,
- leave-one-train-pair-out prediction,
- surprise / prediction error,
- compression and complexity pressure,
- adaptive interaction order,
- ceiling / underdetermination detection,
- post-hoc diagnostics after structure selection.

Forbidden:

- Kaggle submissions,
- `solve(task)` as the organizing abstraction,
- exact-match score as the training objective,
- candidate-ranker score hacking,
- ARC DSL rule libraries,
- test-output inspection during structure selection,
- importing score-lane machinery from older repos.

## Mechanism vocabulary

Prefer:

```text
grow_structure
surprise
compression
chosen_order
ceiling_detected
underdetermined
posthoc_diagnostic
factor_induction
self_induced_factors
```

Avoid:

```text
solve
leaderboard
submission
oracle
score_optimizer
exact_match_objective
```

The language matters because it keeps the mechanism from drifting back into benchmark chasing.

## Conceptual model

The working line is:

```text
impact -> latent trace -> precision gate -> composition -> adaptive order -> ceiling detection
```

In the ARC microscope, this becomes:

```text
train-pair experience -> factors -> interaction space -> leave-one-out surprise -> least sufficient order -> ceiling or commit
```

A good run does not necessarily solve many tasks. A good run shows that the gate climbs when composition is needed, stays simple when simple structure is enough, and refuses to invent structure when the evidence is insufficient.

## Milestone map

### M16 — ARC as ontology microscope

M16 established the minimal diagnostic loop:

- extract train-pair experience,
- build candidate feature spaces by interaction order,
- evaluate each order by leave-one-out surprise,
- penalize complexity,
- choose the least sufficient order,
- report ceiling when no learned order beats the simple baseline.

Observed ARC-50 diagnostic behavior:

```text
order 1: 27
order 2: 9
order 3: 1
none / ceiling: 13
ceiling_rate: 0.26
max_order_rate: 0.02
mean_relative_improvement: ~0.347
regime: healthy_adaptive
```

The important result was not exact-match performance. The important result was that the gate did not blindly climb to maximum order and did not collapse into all-ceiling behavior.

### M16f — parameter stability

A 3x3 lambda/margin sweep stayed stable:

```text
runs: 9
regime_counts: healthy_adaptive = 9
stable_regime: true
mean_ceiling_rate: ~0.256
mean_max_order_rate: ~0.033
mean_relative_improvement: ~0.341
```

This supported the claim that the gate behavior was not only a narrow parameter accident.

### M17 — hierarchical factors

M17 added optional hierarchy/perception factors: scene stats, connected components, bounding boxes, centroids, rank, border contact, density, and simple relations.

This was useful as a perception experiment, but it also exposed the risk of hand-authored semantic leakage. Full hierarchy was stable but not clearly better than basic factors, especially because the feature space became wide and noisy.

### M18 — factor-group ablation

M18 split the hierarchy into named groups and tested them independently.

The diagnostic readout was important:

```text
basic baseline remained strong
full hierarchy hurt relative improvement and increased ceiling rate
only basic + component_color showed a tiny improvement
many standalone hierarchy groups were unstable or ceiling-dominated
```

Interpretation:

```text
Hand-authored hierarchy is not the right final path.
It is a diagnostic probe, not the mechanism.
```

### M19 — self-induced factor space

M19 is the conceptual pivot.

The project should not manually provide objects, groups, rules, deltas, or semantic transformations as input. Those can only be post-hoc names for structures that survived compression.

The induced path starts from a minimal raw substrate:

- pair identity,
- input/output side indicator,
- normalized coordinates,
- centered coordinates,
- color value,
- optional primitive one-hot color coordinates,
- cell index.

From that substrate, the system creates anonymous candidate factors through generic numeric maps such as sparse projections, products of primitive columns, thresholds, and sinusoidal projections. Factors survive only if they reduce train-only surprise after complexity, redundancy, and stability pressure.

The core rule is:

```text
Objects must not be inputs to the mechanism.
Objects may only become post-hoc interpretations of survived structure.
```

### M19 evolution status

The first evolution runner works, but the scientific result must be interpreted carefully. The first uploaded run found improving fitness across generations, but also showed contaminated slice metrics with `insufficient_data` slices. That means the evolution engine is alive, but the stability claim is not accepted until invalid slices are separated from valid metrics.

Current status:

```text
M19 core: accepted
M19 evolution runner: technically works
M19 scientific stability claim: pending
known issue: insufficient_data slices must not be averaged as zero-valued valid runs
```

## What counts as progress

Progress is not a higher leaderboard score.

Progress is:

- lower surprise with controlled complexity,
- lower ceiling rate without max-order explosion,
- stable behavior across seeds and parameter slices,
- better valid-slice relative improvement,
- honest abstention / ceiling behavior under underdetermination,
- post-hoc interpretability of survived factors.

## What counts as failure

Failure modes:

- every task climbs to max order,
- every task becomes ceiling-detected,
- improvements depend on one fragile lambda/margin setting,
- hand-authored semantic groups dominate the result,
- exact-match score silently becomes the objective,
- test outputs influence structure selection,
- docs get overwritten and the research thread is lost.

## Documentation rule

Research documentation is part of the experiment state.

Agents and humans should append dated findings instead of replacing the conceptual record. If a document must be reorganized, preserve the original content in an archive file or a milestone log first.

Do not delete this file unless explicitly requested by the repository owner.
