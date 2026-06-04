# Agent Guardrails

This repo is the clean Ontologic B-lane. Keep the context clean.

## Prime directive

Do not turn this repository into an ARC solver repo.

ARC is allowed only as a microscope for structure growth.

## Required separation

Do not import from old score-lane code such as:

```text
arc_union_orchestrator
arc_evo_operator_lab
arc_candidate_oracle
submission builders
candidate rankers
Kaggle utilities
```

Do not optimise against test exact match.

Do not create submission files.

## Preferred API names

Use:

```text
grow_structure
surprise
chosen_order
ceiling_detected
compression
posthoc_diagnostic
```

Avoid:

```text
solve
score_optimizer
leaderboard
submission
oracle
```

## Implementation guidance

Small, inspectable numpy code is preferred over complex frameworks.

Every selection decision must be explainable from train-pair experience only.

Post-hoc exact/pixel metrics are allowed only after structure has already been chosen.

## Tests to preserve

The test suite must include:

1. synthetic order-1 world -> choose order 1,
2. synthetic order-2 world -> climb to order 2,
3. underdetermined/simple world -> ceiling detection or no aggressive climb,
4. no test-output leakage into selection,
5. no imports from score-lane modules.
