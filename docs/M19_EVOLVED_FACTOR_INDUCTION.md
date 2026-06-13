# M19 Evolved Factor Induction

M19 extends self-induced factor space work with diagnostic tooling for inspecting evolution and ablation JSON reports. These plots are for ontology-microscope inspection only.

## Plotting setup

Plotting is optional and keeps `matplotlib` out of the core runtime dependencies. Install the development and plotting extras when you want static figures:

```bash
pip install -e ".[dev,plot]"
```

## Generate diagnostic plots

```bash
python plot_m19_diagnostics.py \
  --evolution arc_factor_induction_evolution_50_o2.json \
  --ablation arc_induced_factor_ablation_50_o2.json \
  --out-dir plots/m19 \
  --svg
```

The script accepts `--evolution`, `--ablation`, or both. It writes PNG files by default and also writes SVG files when `--svg` is provided.

## Diagnostic scope

The plots are intended to inspect:

- fitness stability,
- ceiling behavior,
- max-order pressure,
- relative improvement,
- feature complexity,
- seed stability,
- regime distribution.

They are not ARC score plots. They are not solver visualizations.
