# Pathway Coverage

## What "5 pathways" means structurally

The professional work that informed this project covered five clinical-imaging pathways.
Each pathway is an independent classification task with its own image characteristics,
feature strategy, and review policy.

The pathways are not variants of one model. Each has its own:

- evaluation plan with separate training, validation, and held-out stages
- calibration and threshold-selection review
- model card and audit evidence
- human-escalation criteria where evidence is insufficient

## Named pathway examples

| Pathway type | Approach | Rationale |
|---|---|---|
| AOM (ear infection) | Hybrid deterministic signals and learned features | Color and texture signals can be reviewed directly alongside learned outputs. |
| Impetigo | Calibrated visual-signal evaluation | Probability calibration and threshold behavior require separate review. |
| Throat analysis | Learned visual-feature model | Appearance variation benefits from learned representations. |
| Insect-bite detection | Pathway-specific visual-signal model | Model and feature choices follow the signal and available evidence. |
| Additional pathways | Mixed | Choices vary with data characteristics and clinical-review needs. |

## How the synthetic demo relates

This repository demonstrates one runnable synthetic pathway. Its pipeline —
`generate_dataset.py` → `train_model.py` → `calibrate_model.py` →
`evaluate_model.py` — makes the evaluation discipline concrete without reproducing private
datasets, model configurations, or operational results.

The evaluation tooling, label-adjudication workflow, and service boundary are deliberately
pathway-agnostic. The public demo provides inspectable artifacts for the synthetic pathway;
private pathway artifacts and performance records are intentionally excluded.
