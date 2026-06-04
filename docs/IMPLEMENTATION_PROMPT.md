# Coding-Agent Implementation Prompt

Implement M16 in this repository without turning it into an ARC solver.

## Goal

Create a minimal Ontologic B-lane diagnostic module that tests whether an adaptive-order compositional gate can grow structure from ARC-style train-pair experience.

Do not optimise Kaggle score. Do not create submissions. Do not import old ARC solver branches.

## Files to implement

- `src/ontologic_core/arc_factors.py`
- `src/ontologic_core/adaptive_order_gate.py`
- `src/ontologic_core/diagnostics.py`
- `arc_ontology_lab.py`
- `tests/test_adaptive_order_gate.py`

## Required behaviour

ARC train pairs are treated as experience. The system must infer the least sufficient factorisation / interaction order needed to predict held-out train pairs under leave-one-out CV.

The objective is internal prediction/surprise minimisation plus complexity control, not exact-match solving.

## Factor extraction

Extract generic ARC factors only:

- normalised x/y coordinate,
- centred x/y coordinate,
- input colour at mapped output coordinate,
- background flag,
- local neighbour same-colour fraction,
- horizontal / vertical / diagonal symmetry partner agreement,
- simple connected-component features,
- output coordinate features.

Avoid task-specific solver primitives.

## Adaptive order

Build feature representations of increasing interaction order:

- order 1: additive independent factors,
- order 2: pairwise interactions,
- order 3: sparse higher interactions.

For each order:

1. run leave-one-out CV over train pairs,
2. train on n-1 pairs,
3. predict the held-out pair,
4. compute surprise / prediction loss,
5. add complexity penalty,
6. choose the least order whose improvement exceeds `margin`,
7. mark `ceiling_detected` if learned structure does not beat a simple prior.

## Post-hoc diagnostics

If test outputs exist, report exact/pixel metrics only after structure selection. Never use test outputs for order choice or training.

## CLI target

```bash
python arc_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --max-order 3 \
  --lambda 1.0 \
  --margin 0.02 \
  --json-out arc_ontology_diag.json
```

## Tests

Add tests for:

1. synthetic order-1 world -> choose order 1,
2. synthetic order-2 world -> climb to order 2,
3. underdetermined/simple world -> ceiling detection or no aggressive climb,
4. test outputs are not used in selection,
5. no imports from old score-lane modules.

## Naming guardrails

Prefer:

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
submission
leaderboard
score_optimizer
oracle
```
