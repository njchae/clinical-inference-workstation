# Methodology

## Dataset policy

All images are synthetic and generated locally from deterministic seeds. This keeps the repo legally simple, reproducible, and clearly separate from any professional dataset.

## Split discipline

The training pipeline uses fixed train, validation, and test partitions.

- Train: fit the tiny model
- Validation: calibration and threshold selection
- Test: final held-out evaluation only

The test split is not used for tuning decisions.

## Hybrid design

The system intentionally mixes:

- deterministic signals from image statistics
- a small learned model family exported as JSON artifacts

This mirrors a pragmatic approach where not every signal needs the same modeling technique.

## Model families

The public demo supports two small model families:

- `baseline_linear`
- `compact_cnn`

Both run through the same split discipline, calibration flow, threshold selection, and artifact export.

## Decision rules

Final triage recommendations are not hardcoded deep in the model. They are driven by [decision_rules.yaml](../configs/decision_rules.yaml), which keeps the policy surface inspectable and easy to review.

## Public command separation

Calibration and evaluation are exposed as separate public commands so reviewers can see that thresholding and held-out evaluation are distinct steps rather than one opaque training script.

## Label review discipline

The labeling workflow keeps weak labels and reviewed labels separate. Structured outputs are validated, low-confidence cases are routed into a manual review queue, and only accepted labels are exported for downstream use.

## Why these evaluation choices matter

These are not bureaucratic steps. Each one exists because skipping it causes a specific, measurable failure in real deployments.

**Skipping calibration** — aggregate ranking metrics can look acceptable while probability
estimates are wrong enough to make the chosen decision threshold unusable. In professional
clinical-image work, calibration review exposed this kind of hidden operating-point failure.
The public synthetic pipeline makes the same review steps explicit without publishing private
datasets or production outcomes.

**Not separating threshold selection from test evaluation** — if the same data is used to both choose the threshold and report final metrics, the threshold is fit to the test set and the reported specificity is optimistic. This is the reason the pipeline uses validation for threshold selection and keeps the test set locked until final evaluation.

**Opening the test set during iteration** — once a model has been compared against held-out test data, those data points are no longer held out. Any subsequent tuning decision informed by test-set performance introduces selection bias into the reported metrics. The pipeline enforces a single test-set evaluation after all tuning is complete.

**Using a single metric (AUC) to declare success** — AUC measures ranking ability, not decision-threshold behavior. A model can achieve high AUC while its probability estimates are so miscalibrated that no useful operating point exists on the ROC curve. Reporting sensitivity, specificity, and calibration together makes the decision-threshold behavior explicit and reviewable.
