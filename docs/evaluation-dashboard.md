# Evaluation Dashboard

## What this demonstrates

The included Streamlit dashboard makes the synthetic pathway's diagnostics reviewable without
requiring a training environment. It models the kind of stakeholder-facing evaluation view
used when technical and non-technical reviewers need the same evidence.

## Capabilities

- Calibration and threshold-sweep views for inspecting probability and decision behavior.
- ROC and model-family comparison views for the synthetic demonstration.
- Bounding-box overlays and review-queue artifacts for inspecting evidence and escalation.
- Static, committed artifacts only: no API keys, clinical images, or private environment access.

## Why calibration is visible

Aggregate ranking metrics alone do not show whether probabilities are suitable for a chosen
decision threshold. The dashboard keeps calibration behavior visible alongside the synthetic
demo's model outputs, reinforcing that evaluation requires more than one headline metric.

## Running the dashboard

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

No model training or API keys are required. The dashboard reads the runnable synthetic
artifacts under `artifacts/latest/`; private pathway results are not included.
