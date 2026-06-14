# ontoLogic

`ontoLogic` is the clean B-lane repository for the Ontologic research line.

This is **not** an ARC-AGI Kaggle solver repository. ARC-style tasks are used only as a diagnostic environment: a small, structured world in which we can observe whether an adaptive gate grows a compact compositional ontology from experience.

```text
ARC is not the goal.
ARC is the microscope.
```

## Canonical research doc

Start here:

- [`ontologic.md`](./ontologic.md) — restored canonical research charter and milestone narrative.
- [`docs/01_MILESTONE_LOG.md`](./docs/01_MILESTONE_LOG.md) — M16 to M19 empirical and conceptual log.
- [`docs/99_AGENT_GUARDRAILS.md`](./docs/99_AGENT_GUARDRAILS.md) — documentation-preservation and B-lane guardrails.

The documentation is part of the experiment state. Do not replace long research notes with short stubs; append or archive instead.

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

- train pairs as experience,
- leave-one-out prediction on train pairs,
- surprise / prediction error,
- compression and complexity pressure,
- adaptive interaction order,
- ceiling / underdetermination detection,
- post-hoc diagnostics after structure selection.

Not allowed:

- Kaggle submissions,
- `solve(task)`-style score optimization,
- ARC exact match as a training objective,
- union orchestrators, DSL score branches, candidate-ranker score hacking,
- inheriting solved-task memory as the mechanism,
- test-output inspection during structure selection,
- deleting or truncating research documentation without explicit instruction.

## Current milestone line

### M16 — ARC as ontology microscope

Minimal diagnostic lab:

1. extract generic ARC factors from train pairs,
2. grow feature interaction order only when leave-one-out surprise improves,
3. choose the least sufficient order,
4. detect ceilings when examples underdetermine the rule,
5. report exact/pixel metrics only as post-hoc diagnostics.

### M17 — hierarchical factors

Added optional human-readable scene/component factor groups. Useful diagnostically, but not the final path.

### M18 — factor-group ablation

Showed that full hierarchy did not reliably improve the gate. Only `basic + component_color` helped slightly; most hand-authored hierarchy groups were neutral, harmful, or unstable.

### M19 — self-induced factor space

Current conceptual pivot:

```text
Objects, groups, and rules must not be inputs.
They may only be post-hoc interpretations of survived latent structure.
```

M19 induces anonymous factors from primitive raw cell observations and keeps only factors that reduce train-only surprise under complexity, redundancy, and stability pressure.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Run the ARC ontology microscope:

```bash
python arc_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --max-order 3 \
  --lambda 1.0 \
  --margin 0.02 \
  --json-out arc_ontology_diag.json
```

Analyze a report:

```bash
python analyze_ontology_report.py \
  --report arc_ontology_diag.json \
  --json-out arc_ontology_analysis.json
```

Run a parameter sweep:

```bash
python sweep_ontology_lab.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --lambdas 0.1,1.0,10.0 \
  --margins 0.005,0.02,0.05 \
  --max-order 3 \
  --json-out arc_ontology_sweep_50.json
```

Run M18 factor-group ablation:

```bash
python ablate_factor_groups.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --max-order 2 \
  --json-out arc_factor_group_ablation_50_o2.json
```

Run M19 induced-factor evolution:

```bash
python evolve_factor_induction.py \
  --data /tmp/arcagi2/data/training \
  --limit 50 \
  --generations 8 \
  --population 16 \
  --max-order 2 \
  --json-out arc_factor_induction_evolution_50_o2.json
```

Generate M19 plots:

```bash
python -m pip install -e ".[dev,plot]"
python plot_m19_diagnostics.py \
  --evolution arc_factor_induction_evolution_50_o2.json \
  --ablation arc_induced_factor_ablation_50_o2.json \
  --out-dir plots/m19 \
  --svg
```

## Repository layout

```text
ontologic.md                         # canonical research charter
AGENTS.md                            # concise agent instructions
docs/
  ONTOLOGIC_B_LANE.md                # original B-lane separation
  M16_ARC_ONTOLOGY_MICROSCOPE.md     # microscope spec and analyzer notes
  M17_HIERARCHICAL_FACTORS.md        # hierarchy/perception experiment
  M18_FACTOR_GROUP_ABLATION.md       # factor-group ablation protocol
  M19_SELF_INDUCED_FACTOR_SPACE.md   # induced factor-space concept
  M19_EVOLVED_FACTOR_INDUCTION.md    # M19 evolution/plot tooling
  01_MILESTONE_LOG.md                # preserved research progression
  99_AGENT_GUARDRAILS.md             # documentation and B-lane guardrails
src/ontologic_core/
  adaptive_order_gate.py             # self-calibrating adaptive-order gate
  arc_factors.py                     # basic/hierarchical/induced factor extraction
  arc_hierarchy.py                   # optional hierarchy analysis
  factor_induction.py                # anonymous induced factor space
  report_analysis.py                 # diagnostic report interpretation
  sweep_analysis.py                  # sweep-level regime analysis
tests/                               # mechanism and boundary tests
```

## Development stance

Implementation passing tests is not enough for scientific acceptance.

Use two separate labels:

```text
implementation: accepted / pending
scientific result: accepted / pending / rejected
```

A result is scientifically accepted only when the diagnostic metrics support the claim without test leakage, metric contamination, or fragile parameter dependence.
