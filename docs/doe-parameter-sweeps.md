# DOE Parameter Sweeps

The pipeline selects an operating point in two steps that already scan a range of
values: `calibrate_model_artifacts()` fits a temperature by scanning a
temperature range (`_fit_temperature`), then picks the review threshold that
maximizes specificity subject to a sensitivity floor (`_find_threshold`), both in
[`src/clinical_inference_workstation/ml/pipeline.py`](../src/clinical_inference_workstation/ml/pipeline.py).

The DOE harness generalizes that selection into a **design-of-experiments grid
sweep**: evaluate every `(temperature, threshold)` combination in a configured
matrix, record the resulting sensitivity / specificity / accuracy per cell, and
report the best cell that clears the sensitivity target. This makes the parameter
space and its trade-offs inspectable in one artifact instead of one run at a time.

## What it produces

Running the sweep writes two artifacts alongside the model:

- [`artifacts/latest/doe_results.csv`](../artifacts/latest/doe_results.csv) — one
  row per cell: the factor levels, the three metrics, whether the cell met the
  sensitivity target, and the objective (specificity when the target is met).
- [`artifacts/latest/doe_summary.json`](../artifacts/latest/doe_summary.json) —
  the grid definition, the target, the selected best cell, and the committed
  pipeline configuration for side-by-side comparison.

A rendered example is committed at
[`artifacts/latest/report_example.md`](../artifacts/latest/report_example.md).

## Design

Factors and objective live in
[`configs/doe/threshold_sweep.yaml`](../configs/doe/threshold_sweep.yaml):

```yaml
design: full_factorial          # or fractional_factorial
factors:
  temperature: [0.8, 1.0, 1.2, 1.5, 2.0]
  threshold: [0.30, 0.40, 0.45, 0.50, 0.60]
objective:
  target_sensitivity: 0.70
  maximize: specificity
```

- `build_full_factorial` enumerates the full Cartesian product of factor levels.
- `build_fractional_factorial` takes a deterministic every-*k*-th subset to cut
  cost on large grids. It is a simple reproducible fraction, not a formal
  resolution-III/IV design.

Cell scoring reuses the pipeline's own primitives — `apply_temperature` and
`binary_metrics` — so a swept cell is scored the same way the committed
configuration is. The objective mirrors `_find_threshold`: maximize specificity
among cells that clear the sensitivity floor, breaking ties toward the more
conservative (lower) threshold.

## Split discipline

The sweep runs on the **validation** split by default (`--split validation`). The
held-out test set stays locked, so exploring the parameter grid never touches the
data reserved for final evaluation. This is the same no-leakage separation the
rest of the pipeline follows.

## Running it

```bash
# Sweep the grid on the validation split, write CSV + summary
python scripts/run_doe_sweep.py --split validation

# Render the Markdown report (metrics + calibration + best swept cell)
python scripts/generate_report.py

# Or via the task runner
make sweep report
```

## Visualizing the sweep

The Streamlit evaluation dashboard renders the sweep as a temperature × threshold
heatmap (select the metric — specificity, sensitivity, or accuracy — and the best
target-meeting cell is marked). It reads `doe_results.csv` directly:

```bash
make dashboard   # streamlit run dashboard/app.py
```

The pivot logic lives in
[`src/clinical_inference_workstation/doe/grid.py`](../src/clinical_inference_workstation/doe/grid.py)
and is unit-tested independently of the UI.
