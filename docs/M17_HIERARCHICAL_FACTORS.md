# M17 hierarchical ARC factors

M17 adds an optional richer factor-extraction mode for the Ontologic B-lane ARC
microscope. The purpose is perception enrichment: train-pair experience can now
include scene, object, and simple relational measurements from the input canvas
before the existing adaptive-order gate chooses a structure-growth order.

## Factor modes

- `basic` keeps the M16 factor vector unchanged and remains the default.
- `hierarchical` appends M17 factors to the basic vector.

The hierarchical factors are derived only from each train input grid, the mapped
cell coordinate, and the known train output target for that represented row. M17
analyses same-colour 4-neighbourhood connected components, background colour,
foreground density, component bounding boxes, centroids, area/rank flags, border
contact, and simple cell-to-component/global-center relations.

## Not a solver

M17 does not add output construction, task-specific ARC transforms, candidate
generation, held-out-answer inspection, or score-driven tuning. ARC remains the
microscope for observing structure growth. The diagnostic output is the
adaptive-order behavior and post-hoc report summaries, not task answers.

## Before/after comparison

Run the stable M16 basic factor sweep:

```bash
python sweep_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --lambdas 0.1,1.0,10.0 \
  --margins 0.005,0.02,0.05 \
  --max-order 3 \
  --factor-mode basic \
  --json-out arc_ontology_sweep_50_basic.json
```

Run the M17 hierarchical factor sweep:

```bash
python sweep_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --lambdas 0.1,1.0,10.0 \
  --margins 0.005,0.02,0.05 \
  --max-order 3 \
  --factor-mode hierarchical \
  --json-out arc_ontology_sweep_50_hierarchical.json
```

M17 should be evaluated by gate-regime health: hierarchical mode should keep the
dominant regime `healthy_adaptive` or conservatively adjacent, avoid
`over_climbing`, avoid a large `max_order_rate` increase, and ideally lower
`ceiling_rate` or improve `mean_relative_improvement`. It is not judged by ARC
exact-match accuracy.
