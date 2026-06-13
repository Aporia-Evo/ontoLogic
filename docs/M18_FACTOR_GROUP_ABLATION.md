# M18 factor-group ablation

M17 added a full hierarchical factor mode and kept it stable, especially when the
microscope is run with `--max-order 2`. The scientific readout was not yet
beneficial: the full appended hierarchy increased `ceiling_rate` and slightly
reduced `mean_relative_improvement` compared with `basic`. That suggests the raw
hierarchy bundle is too broad, noisy, or expensive under the current complexity
pressure.

M18 therefore splits hierarchical perception into named factor groups so each
piece can be tested independently.

## Factor groups

The groups are:

- `basic`
- `scene_stats`
- `component_geometry`
- `component_rank`
- `component_color`
- `component_bbox_relation`
- `component_centroid_relation`
- `global_geometry`
- `local_density`
- `hole_or_enclosure`

`mode="basic"` remains unchanged and uses only `basic`. `mode="hierarchical"`
without `factor_groups` uses all groups. Supplying `--factor-groups` in
hierarchical mode keeps only those groups, in deterministic canonical order.
Reports include the active group list and deterministic feature widths.

## ARC remains the microscope

M18 does not add output construction, task-specific transforms, held-out-answer
selection, or score tuning. It only asks which perception groups compress
train-pair experience in a healthier way for the unchanged adaptive-order gate.

## Run a group ablation

```bash
python ablate_factor_groups.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --max-order 2 \
  --lambdas 0.1,1.0,10.0 \
  --margins 0.005,0.02,0.05 \
  --json-out arc_factor_group_ablation_50_o2.json
```

The report contains a `baseline` block for `basic` and a `runs` list for:

- each hierarchy group alone,
- `basic` plus each hierarchy group,
- `basic` plus selected group pairs,
- full hierarchical extraction.

Each run reports dominant regime, regime counts, mean ceiling rate, mean max
order rate, mean relative improvement, deltas versus `basic`, and a verdict:

- `helps`: ceiling rate decreases or relative improvement increases while the
  regime remains healthy and max-order usage stays controlled,
- `hurts`: ceiling rate increases and relative improvement decreases,
- `unstable`: the dominant regime moves away from `healthy_adaptive` or max-order
  usage jumps sharply,
- `neutral`: changes are small or inconclusive.
