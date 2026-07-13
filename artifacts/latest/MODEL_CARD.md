# Model Card

## Summary

This public demo model detects a synthetic concerning pattern from generated triage-style images.

- Model family: baseline_linear

## Data

- Fully synthetic images generated locally
- Non-diagnostic public demo
- Intended to demonstrate methodology and system design, not clinical accuracy

## Metrics

- Sensitivity: 1.0000
- Specificity: 1.0000
- Accuracy: 1.0000

These scores reflect held-out performance on synthetic data where the visual task is
engineered to be solvable by design. Calibration, sensitivity-constrained threshold
selection, and locked test evaluation are separate steps in the pipeline.

## Calibration

Temperature scaling is applied to correct probability estimates before threshold selection.
The calibration temperature (0.50) reflects how the model's raw probabilities
compare to the true class distribution — values below 1.0 indicate the model was
underconfident (probabilities clustered near 0.5); values above 1.0 indicate overconfidence.

On this synthetic task the visual signal is strong enough that calibration does not change
classification outcomes. In professional clinical-image work, the same methodology exposed
threshold behavior that an aggregate ranking metric alone would not reveal. Private datasets
and production outcomes are intentionally omitted here.

See `docs/methodology.md` and `artifacts/latest/calibration.json` for more detail.

## Deployment knobs

- Review threshold: 0.37
- Calibration temperature: 0.50
