# M16 — ARC as Ontology Microscope

## Claim under test

A gate can use sparse ARC-style experience to grow a compact compositional structure, choose the least sufficient interaction order, and detect underdetermination without using ARC score as an objective.

## Inputs

ARC-style JSON tasks:

```json
{
  "train": [{"input": [[...]], "output": [[...]]}],
  "test": [{"input": [[...]], "output": [[...]]}]
}
```

Only `train` pairs are used for structure selection.

`test.output`, when present, is used only for post-hoc diagnostics.

## Required module shape

Implement:

```text
src/ontologic_core/arc_factors.py
src/ontologic_core/adaptive_order_gate.py
src/ontologic_core/diagnostics.py
arc_ontology_lab.py
tests/test_adaptive_order_gate.py
```

## Required public language

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
```

## Minimal algorithm

For each task:

1. Convert train pairs into pixel-level experience.
2. Extract generic factors:
   - normalised x/y coordinate,
   - centered x/y coordinate,
   - input colour at mapped coordinate,
   - background flag,
   - neighbour same-colour fraction,
   - symmetry partner colours,
   - simple connected-component stats.
3. Build order-1 feature space.
4. Build order-2 pairwise interactions.
5. Build sparse order-3 interactions.
6. For each order, run leave-one-out CV over train pairs.
7. Compute surprise and complexity.
8. Choose the least order whose CV improvement exceeds `margin`.
9. Detect ceiling if no learned order beats a simple prior by `margin`.
10. Optionally report test pixel/exact as post-hoc microscope.

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

## JSON output target

```json
{
  "summary": {
    "tasks": 50,
    "mean_chosen_order": 1.8,
    "order_counts": {"1": 20, "2": 25, "3": 5},
    "ceiling_detected": 7,
    "mean_cv_surprise": 0.42,
    "mean_complexity": 0.03,
    "diagnostic_exact": 3,
    "diagnostic_pixel_acc": 0.61
  },
  "tasks_detail": []
}
```


## M16c status — ARC ontology lab runner

M16c adds `arc_ontology_lab.py`, a diagnostic runner for ARC-style task directories. The runner:

1. loads `*.json` tasks from `--data`, with optional `--limit`;
2. extracts only `train` pair experience with `arc_factors.extract_task_experience()`;
3. calls `AdaptiveOrderGate.grow_structure()` using `--max-order`, `--lambda`, and `--margin`;
4. writes a JSON report with per-task `chosen_order`, `ceiling_detected`, `selected_reason`, `cv_curve`, `final_surprise`, and `final_complexity`;
5. records per-task errors without stopping the whole lab run.

This remains a microscope diagnostic, not a prediction pipeline. Test outputs are not needed for structure selection, and no held-out answers are read by the runner.

### M16c usage

```bash
python arc_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --max-order 3 \
  --lambda 1.0 \
  --margin 0.02 \
  --json-out arc_ontology_diag.json
```

The output shape is:

```json
{
  "summary": {
    "tasks": 50,
    "ok": 50,
    "errors": 0,
    "order_counts": {"1": 20, "2": 25, "3": 5, "none": 0},
    "ceiling_detected": 7,
    "mean_chosen_order": 1.8,
    "mean_final_surprise": 0.42,
    "mean_final_complexity": 0.03
  },
  "tasks_detail": []
}
```

## Kill criteria

- If order growth always climbs to max order, the gate is overfitting.
- If order growth never climbs even on synthetic order-2 worlds, the representation is too weak.
- If ceiling detection never triggers on underdetermined/noise worlds, the precision/compression control is broken.
- If implementation uses test outputs for selection, the B-lane boundary is violated.
