# Agent Guardrails

This repo is the clean Ontologic B-lane. Keep the context clean.

```text
ARC is not the goal. ARC is the microscope.
```

## Prime directive

Do not turn this repository into an ARC solver repo.

ARC is allowed only as a microscope for structure growth.

## Documentation preservation

Research documentation is part of the experiment state.

Do not delete, truncate, or replace:

- `README.md`,
- `ontologic.md`,
- `docs/*.md`,
- milestone logs,
- research-charter text,
- guardrail documents.

When editing docs, prefer appending dated or milestone-specific sections. If a document must be reorganized, preserve old content in an archive, milestone log, or replacement section first.

Never replace a long research document with a short stub unless the repository owner explicitly asks for that.

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
factor_induction
self_induced_factor_space
```

Avoid:

```text
solve
score_optimizer
leaderboard
submission
oracle
exact_match_objective
```

## Implementation guidance

Small, inspectable numpy code is preferred over complex frameworks.

Every selection decision must be explainable from train-pair experience only.

Post-hoc exact/pixel metrics are allowed only after structure has already been chosen.

Implementation passing tests is not the same as scientific acceptance. Reports should distinguish:

```text
implementation: accepted / pending
scientific result: accepted / pending / rejected
```

## Tests to preserve

The test suite must include:

1. synthetic order-1 world -> choose order 1,
2. synthetic order-2 world -> climb to order 2,
3. underdetermined/simple world -> ceiling detection or no aggressive climb,
4. no test-output leakage into selection,
5. no imports from score-lane modules,
6. no deletion/truncation of core research docs.
