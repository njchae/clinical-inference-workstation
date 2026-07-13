# 5-7 Minute Demo Walkthrough

A guided tour of the repo. Each step names what to open and what it shows.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/bootstrap_demo.py
python scripts/run_api.py
```

Open `http://127.0.0.1:8000/`.

## Demo Flow

### 0. Start with the calibration result

Open:

- [`artifacts/latest/calibration.json`](../artifacts/latest/calibration.json)
- [`artifacts/latest/MODEL_CARD.md`](../artifacts/latest/MODEL_CARD.md)

What this shows:

The repo treats calibration as a mandatory pipeline step, not an afterthought. The model
card explains why — on this synthetic demo, calibration does not change outcomes because the
task is engineered to be solvable. In professional work, the same review pattern exposed
probability-calibration failures that aggregate metrics alone did not reveal. This public
demo keeps the method inspectable without publishing private evaluation results.

### 1. Open the workstation

Show:

- the sample cards
- the upload flow — any PNG can be run through the full pipeline live, so a demo is not
  limited to the committed synthetic samples
- the case view with the detected signal-region overlay
- the decision summary panel

What this shows:

The repo is not just a model dump. It includes an operator-facing review surface for
interacting with inference results. In the private system, the equivalent was the thin
internal tooling layer that sits on top of applied ML services.

### 2. Click `Concerning pattern`

Show:

- the case view overlay with the localized signal region
- the signal breakdown bars with the decision-threshold tick
- the populated decision summary

What this shows:

The triage recommendation is presented as a combination of deterministic signals plus
calibrated model output — an inspectable workflow rather than a black-box prediction
endpoint.

### 3. Show the API response artifact

Open:

- [`artifacts/latest/api_response_example.json`](../artifacts/latest/api_response_example.json)

What this shows:

The service returns request metadata, model metadata, signal values, localized region, and
thresholded decision output in one inspectable response — the service-contract and
observability shape applied in production-minded ML work.

### 4. Show the audit log example

Open:

- [`output/inference_audit.jsonl`](../output/inference_audit.jsonl)
- [`artifacts/latest/audit_log_example.jsonl`](../artifacts/latest/audit_log_example.jsonl)

What this shows:

Inference actions are persisted with request IDs and decision data rather than disappearing
after the HTTP response — the public-safe analogue of auditability and traceability
requirements in real clinical systems.

### 5. Show the model artifacts

Open:

- [`artifacts/latest/MODEL_CARD.md`](../artifacts/latest/MODEL_CARD.md)
- [`artifacts/latest/metrics.json`](../artifacts/latest/metrics.json)
- [`artifacts/latest/thresholds.json`](../artifacts/latest/thresholds.json)

What this shows:

Training, calibration, and evaluation produce separate reviewable outputs — evaluation
discipline and artifact packaging rather than a one-shot notebook workflow.

### 6. Show the labeling workflow artifacts

Open:

- [`artifacts/latest/review_queue_example.jsonl`](../artifacts/latest/review_queue_example.jsonl)
- [`artifacts/latest/reviewed_labels_example.json`](../artifacts/latest/reviewed_labels_example.json)

Optional commands:

```bash
python scripts/label_images.py --images-dir web/samples --provider local --checkpoint-path output/labels/checkpoint.json --output-path output/labels/results.json --review-queue-path output/labels/review_queue.jsonl
python scripts/export_reviewed_labels.py --labels-path output/labels/results.json --export-path output/labels/training_labels.json
```

What this shows:

The repo includes a machine-assisted labeling path with explicit human-review handoff and
reviewed-label export — the workflow pattern used for LLM-assisted labeling in the private
system, without publishing proprietary prompts or internal tools.

### 7. Show the adjudication trace

Open:

- [`docs/agentic-adjudication.md`](agentic-adjudication.md)
- [`artifacts/latest/adjudication_result_example.json`](../artifacts/latest/adjudication_result_example.json)
- [`artifacts/latest/adjudication_trace_example.json`](../artifacts/latest/adjudication_trace_example.json)
- [`artifacts/latest/adjudication_escalation_example.jsonl`](../artifacts/latest/adjudication_escalation_example.jsonl)

What this shows:

The repo does not just have provider-shaped stubs. It includes staged prompt contracts,
policy checking, structured outputs, and explicit routing to `needs_human_review` —
LLM orchestration as a bounded engineering workflow rather than a generic chat wrapper.

## Close

Finish with the capability map:

- [Capability Map](capability-map.md)

For deeper technical detail:

- [Architecture](architecture.md)
- [Methodology](methodology.md)
- [Deployment](deployment.md)
