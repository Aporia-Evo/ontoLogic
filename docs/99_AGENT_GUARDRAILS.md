# Agent Guardrails for Ontologic

This repository is a research record as well as a codebase. Do not optimize the code while erasing the thinking that explains why the code exists.

## Prime directive

```text
ARC is not the goal. ARC is the microscope.
```

Do not turn this repository into an ARC solver repository.

## Documentation preservation rule

Do not delete, truncate, or replace research documentation unless explicitly instructed by the repository owner.

This includes:

- `README.md`,
- `ontologic.md`,
- files under `docs/`,
- milestone logs,
- experiment reports,
- research-charter text,
- guardrail documents.

When editing docs:

1. Prefer appending dated or milestone-specific sections.
2. Preserve old conceptual text unless it is factually wrong.
3. If reorganizing, move old content into an archive or milestone file first.
4. Never replace a long research document with a short stub.
5. Never remove the B-lane boundary language.

## Forbidden drift

Do not add or encourage:

- Kaggle submissions,
- leaderboard tuning,
- `solve(task)` as the primary abstraction,
- exact-match score as the objective,
- candidate-ranker score hacking,
- ARC DSL rule libraries,
- test-output leakage into selection,
- imports from older score-lane modules.

## Preferred language

Use:

```text
grow_structure
surprise
compression
complexity pressure
chosen_order
ceiling_detected
underdetermined
posthoc_diagnostic
factor_induction
self_induced_factor_space
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

## Scientific acceptance rule

Implementation passing tests is not the same as scientific acceptance.

Use this distinction in reports:

```text
implementation: accepted / pending
scientific result: accepted / pending / rejected
```

A milestone is scientifically accepted only when diagnostics support the claim without obvious leakage, metric contamination, or fragile parameter dependence.

## Current open caution

M19 evolution currently needs valid-slice metric handling. `insufficient_data` slices must not be averaged as zero-valued valid runs. They should be reported and penalized separately.
