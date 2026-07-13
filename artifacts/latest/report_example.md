# Algorithm Configuration Report

Generated from committed evaluation artifacts. Synthetic demo data — interpret as pipeline validation, not clinical performance.

## Held-out Metrics

| Metric | Value |
| --- | --- |
| Sensitivity | 1.0000 |
| Specificity | 1.0000 |
| Accuracy | 1.0000 |

## Calibration & Threshold

- Calibration temperature: `0.5`
- Review threshold: `0.37`

## Model-family Comparison

- Trained family: `baseline_linear`
- Available families: `baseline_linear`, `compact_cnn`

## Best Swept Configuration

- Cells evaluated: 25
- Sensitivity target: 0.7
- Best cell: temperature=0.8, threshold=0.45
- At best cell — Sensitivity 1.0000, Specificity 1.0000, Accuracy 1.0000
- Committed pipeline configuration: temperature `0.5`, review threshold `0.37`
