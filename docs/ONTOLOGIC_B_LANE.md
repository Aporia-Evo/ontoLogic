# Ontologic B-Lane

## Purpose

This repository is the clean Ontologic B-lane. It exists to test a mechanism, not to win a benchmark.

ARC-like tasks are useful because they expose objecthood, relation, composition, underdetermination, and generalisation from sparse experience. They are not the objective.

## Non-negotiable separation

Score-lane question:

```text
How can we increase ARC-AGI exact match?
```

B-lane question:

```text
Does a gate grow the least sufficient structure from experience?
Does it choose its own interaction order?
Does it stop before overfitting?
Can it detect when the examples underdetermine the rule?
```

## Mechanism target

The first clean mechanism should:

1. extract generic factors from ARC train pairs,
2. create feature spaces of increasing interaction order,
3. evaluate each order only by leave-one-out prediction on train experience,
4. penalise complexity,
5. choose the least order that improves surprise beyond a margin,
6. flag a ceiling if the learned structure does not beat the prior/simple baseline.

This corresponds to the Ontologic line:

```text
impact -> latent trace -> precision gate -> composition -> adaptive order -> ceiling detection
```

## What exact match means here

Exact match and pixel accuracy are post-hoc diagnostics only. They are allowed as a microscope after structure growth, not as training pressure.

## Terms

- **surprise**: predictive loss on held-out experience.
- **prior precision / lambda**: resistance to overfitting noisy experience.
- **margin**: growth aggressiveness; how much better a higher order must be before the gate climbs.
- **chosen order**: the interaction depth justified by experience.
- **ceiling detected**: the experience does not support a structure better than the prior/simple baseline.

## Forbidden imports

This repo should not import or depend on score-lane modules such as union orchestrators, candidate rankers, submission builders, or ARC-specific DSL score hacks.
