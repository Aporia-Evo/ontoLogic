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

## M16d status — ontology-lab analysis layer

M16d adds a post-hoc analysis layer for the diagnostic JSON written by the ARC ontology microscope. It reads `arc_ontology_diag.json` and summarizes whether the adaptive-order gate looks like a conservative structure-growth mechanism, a max-order climber, an under-climber, or a ceiling-heavy factorization.

The analyzer reports:

1. `chosen_order` distribution, including `none` for ceilings;
2. `ceiling_detected` rate over successful task diagnostics;
3. mean surprise and complexity by candidate order from the recorded CV curves;
4. how often the chosen structure reaches the maximum recorded order;
5. a gate regime label:
   - `healthy_adaptive`,
   - `over_climbing`,
   - `under_climbing`,
   - `ceiling_dominated`,
   - `too_many_errors`,
   - `insufficient_data`;
6. interesting tasks for inspection, including ceilings, max-order choices, large surprise improvements, slight rejected higher-order improvements, and task errors.

This remains an interpretability layer. It does not change the gate, factor extraction, or lab runner, and it does not predict ARC outputs.

### M16d usage

```bash
python arc_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --max-order 3 \
  --lambda 1.0 \
  --margin 0.02 \
  --json-out arc_ontology_diag.json

python analyze_ontology_report.py \
  --report arc_ontology_diag.json \
  --json-out arc_ontology_analysis.json \
  --top 20
```

The analysis output shape is:

```json
{
  "summary": {
    "tasks": 50,
    "ok": 48,
    "errors": 2,
    "regime": "healthy_adaptive",
    "order_counts": {"1": 18, "2": 20, "3": 5, "none": 5},
    "ceiling_rate": 0.10416666666666667,
    "max_order_rate": 0.10416666666666667,
    "mean_final_surprise": 0.42,
    "mean_relative_improvement": 0.31,
    "mean_surprise_by_order": {"1": 0.53, "2": 0.45, "3": 0.44},
    "mean_complexity_by_order": {"1": 0.01, "2": 0.02, "3": 0.03}
  },
  "interpretation": [
    "regime: healthy_adaptive",
    "order_distribution: order 1=18, order 2=20, order 3=5, order none=5"
  ],
  "interesting_tasks": [
    {
      "task": "example_task",
      "reason": "ceiling_detected",
      "chosen_order": null,
      "ceiling_detected": true,
      "relative_improvement": 0.0,
      "selected_reason": "ceiling_detected: no learned order beat the baseline surprise"
    }
  ]
}
```

Use the regime and interesting-task list to decide the next scientific step: tune complexity pressure, inspect factor weakness, or broaden the task sample. The analyzer should not be used as an objective for exact-match improvement.

## M16f status — parameter stability sweep

M16f adds a lambda/margin sweep for the ontology microscope. The sweep asks whether the qualitative `healthy_adaptive` regime is stable across nearby regularization and structure-growth margin settings. It is explicitly a stability diagnostic, not a route for improving exact-match outcomes.

The sweep runner:

1. iterates over every requested `lambda` and `margin` pair;
2. calls `arc_ontology_lab.run_lab()` for each pair using train-pair experience only;
3. calls `report_analysis.analyze_report()` on each diagnostic report;
4. records the compact post-hoc fields needed to compare qualitative behavior:
   - `regime`,
   - `order_counts`,
   - `ceiling_rate`,
   - `max_order_rate`,
   - `mean_final_surprise`,
   - `mean_relative_improvement`;
5. summarizes whether most rows remain `healthy_adaptive` or conservatively adjacent, and flags narrow or extreme regime flips.

### M16f usage

```bash
python sweep_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --lambdas 0.1,1.0,10.0 \
  --margins 0.005,0.02,0.05 \
  --max-order 3 \
  --json-out arc_ontology_sweep_50.json
```

The sweep output shape is:

```json
{
  "summary": {
    "runs": 9,
    "stable_regime": true,
    "dominant_regime": "healthy_adaptive",
    "regime_counts": {"healthy_adaptive": 8, "under_climbing": 1},
    "notes": ["most rows are healthy_adaptive or conservatively adjacent"]
  },
  "runs": [
    {
      "lambda": 1.0,
      "margin": 0.02,
      "regime": "healthy_adaptive",
      "order_counts": {"1": 18, "2": 20, "3": 5, "none": 5},
      "ceiling_rate": 0.10416666666666667,
      "max_order_rate": 0.10416666666666667,
      "mean_final_surprise": 0.42,
      "mean_relative_improvement": 0.31
    }
  ]
}
```

Classification guidance:

- `stable_regime=true` when most rows are `healthy_adaptive` or conservatively adjacent, without an extreme flip.
- `insufficient_data` rows are not evidence of stability; an all-insufficient sweep is reported as non-stable because parameter stability cannot be assessed.
- Extreme flips are flagged when rows include both `over_climbing` and `ceiling_dominated`.
- A narrow single `healthy_adaptive` row is treated as fragile rather than stable.

M16f should be used to check robustness of the microscope setting, not to tune for held-out exactness. The gate still chooses structure only from train-pair experience, and the sweep records only post-hoc diagnostic aggregates.
