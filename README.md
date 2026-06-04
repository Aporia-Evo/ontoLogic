# ontoLogic

`ontoLogic` is the clean B-lane repository for the Ontologic research line.

This is **not** an ARC-AGI Kaggle solver repository. ARC-style tasks are used only as a diagnostic environment: a small, structured world in which we can observe whether an adaptive gate grows a compact compositional ontology from experience.

## Core question

Not:

```text
How many ARC tasks can this solve?
```

But:

```text
Can a self-calibrating, adaptive-order gate grow the least sufficient internal structure from experience, stop before overfitting, and detect underdetermination?
```

## B-lane rules

Allowed:

- train pairs as experience
- leave-one-out prediction on train pairs
- surprise / prediction error
- compression and complexity pressure
- adaptive interaction order
- ceiling / underdetermination detection
- post-hoc exact/pixel diagnostics when outputs are available

Not allowed:

- Kaggle submissions
- `solve(task)`-style score optimisation
- ARC exact match as a training objective
- union orchestrators, DSL score branches, candidate-ranker score hacking
- inheriting solved-task memory as the mechanism

## Current milestone

**M16 — ARC as ontology microscope**

Build a minimal diagnostic lab that asks whether structure grows from experience:

1. extract generic ARC factors from train pairs,
2. grow feature interaction order only when leave-one-out surprise improves,
3. choose the least sufficient order,
4. detect ceilings when examples underdetermine the rule,
5. report test exact/pixel metrics only as post-hoc diagnostics.

## Intended layout

```text
src/ontologic_core/       # mechanism code: gate, factors, diagnostics
docs/                     # B-lane charter and milestone specs
tests/                    # mechanism tests, not benchmark-score tests
arc_ontology_lab.py       # future CLI microscope, not a solver
```

## Development stance

ARC is not the goal. ARC is the microscope.
