# Capability Map

This file maps major capability categories to concrete public evidence in this repo.

## Auth-aware inference API

- `src/clinical_inference_workstation/api/auth.py`
- `src/clinical_inference_workstation/api/router.py`
- `tests/api/test_auth_and_audit.py`
- `artifacts/latest/api_response_example.json`

## Audit logging and inference persistence

- `src/clinical_inference_workstation/api/audit.py`
- `src/clinical_inference_workstation/api/service.py`
- `tests/api/test_auth_and_audit.py`
- `artifacts/latest/audit_log_example.jsonl`

## Machine-assisted labeling workflow

- `src/clinical_inference_workstation/labeling/providers.py`
- `src/clinical_inference_workstation/labeling/pipeline.py`
- `scripts/label_images.py`
- `scripts/export_reviewed_labels.py`
- `tests/unit/test_labeling_pipeline.py`
- `artifacts/latest/review_queue_example.jsonl`
- `artifacts/latest/reviewed_labels_example.json`

## Agentic adjudication workflow

- `docs/agentic-adjudication.md`
- `configs/adjudication_prompts/`
- `src/clinical_inference_workstation/labeling/adjudication.py`
- `src/clinical_inference_workstation/labeling/adjudication_providers.py`
- `scripts/run_adjudication_workflow.py`
- `tests/unit/test_adjudication_workflow.py`
- `artifacts/latest/adjudication_result_example.json`
- `artifacts/latest/adjudication_trace_example.json`
- `artifacts/latest/adjudication_escalation_example.jsonl`
- `artifacts/latest/adjudication_comparison_example.json`

## Model evaluation discipline

- `src/clinical_inference_workstation/ml/pipeline.py`
- `tests/unit/test_model_pipeline.py`
- `docs/methodology.md`
- `artifacts/latest/metrics.json`
- `artifacts/latest/thresholds.json`
- `artifacts/latest/MODEL_CARD.md`

## DOE parameter sweeps

- `src/clinical_inference_workstation/doe/matrix.py`
- `src/clinical_inference_workstation/doe/sweep.py`
- `src/clinical_inference_workstation/doe/grid.py`
- `scripts/run_doe_sweep.py`
- `configs/doe/threshold_sweep.yaml`
- `docs/doe-parameter-sweeps.md`
- `artifacts/latest/doe_results.csv`
- `artifacts/latest/doe_summary.json`

## Deployable service shape

- `Dockerfile`
- `.github/workflows/ci.yml`
- `.github/workflows/azure-deploy.yml`
- `scripts/verify_deployment.py`
- `docs/deployment.md`

## Evaluation dashboard and stakeholder diagnostics

- `docs/evaluation-dashboard.md`
- `artifacts/latest/calibration.json`
- `artifacts/latest/review_queue_example.jsonl`
- `artifacts/latest/MODEL_CARD.md`

## Multi-pathway system structure

- `docs/pathway-coverage.md`
- `artifacts/latest/comparison.json`

## Project context and walkthrough

- `docs/portfolio-context.md`
- `docs/demo-walkthrough.md`

## Operator-facing workstation

- `web/index.html`
- `web/app.js`
- `tests/e2e/workstation.spec.js`
- `artifacts/latest/workstation-demo.png`
