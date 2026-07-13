# Agentic Adjudication

This repo includes one deep, engineering-first agentic workflow: structured label adjudication.

It orchestrates model-assisted work with explicit contracts, bounded stages, and human-review routing rather than letting a model make the final call by itself.

## Workflow shape

The adjudication workflow runs after weak labeling and before reviewed-label export.

Stages:

- `evidence_collector`
- `label_reviewer`
- `safety_checker`
- `review_router`

Each stage has:

- a prompt template committed in `configs/adjudication_prompts/`
- explicit allowed tools
- structured stage output
- inclusion in an auditable workflow trace

## Final decisions

The workflow produces one of:

- `accept`
- `needs_human_review`
- `reject_for_insufficient_evidence`

The public demo is deliberately conservative. Its main visible behavior is escalation to `needs_human_review` when the evidence is weak or conflicting.

## Why this is orchestration, not prompt chaining

**Naive prompt chaining** would concatenate the evidence into one prompt and ask for a
final label decision. There is no schema contract between steps, no validation before the
next step executes, no way to inspect intermediate reasoning, and failure is silent — a
bad intermediate output propagates forward without surfacing.

**This workflow** treats each stage as a bounded contract:

- each stage has a committed prompt template, a declared allowed-tool list, and a validated
  output schema
- the output of each stage is validated against the schema before the next stage receives it
  — if a stage breaks the contract, the workflow surfaces the error rather than continuing
- the full trace is committed as an artifact so any reviewer can audit the reasoning at every
  stage, not just the final decision
- three explicit outcomes (`accept`, `needs_human_review`,
  `reject_for_insufficient_evidence`) ensure the system cannot silently accept cases it
  cannot evaluate — poor-quality inputs are rejected at the workflow level rather than
  queued for a human reviewer who cannot resolve the underlying data problem

This pattern was informed by professional work on LLM-assisted clinical-image labeling using
structured outputs and clinician-review escalation. The public implementation demonstrates
the orchestration and audit boundaries without publishing private agreement measurements,
review rates, or source data.

## Provider abstraction

Every stage runs behind a single `AdjudicationProvider` interface
(`run_case(label) -> AdjudicationResult`), selected by a factory:

- **local** — a deterministic adapter that runs the full four-stage workflow with no network
  access or credentials, so CI exercises the real orchestration and the committed example
  artifacts are reproducible.
- **openai / anthropic** — adapters that define the LLM-API integration boundary: API keys are
  read from environment variables and each stage emits a schema-validated structured output.
  Live calls are intentionally not exercised in the public demo, so no credentials or private
  endpoints are embedded.

Each stage loads its committed prompt template from `configs/adjudication_prompts/`, declares
an allowed-tool list, and returns a structured output that is validated before the next stage
runs. The prompt templates are the versioned contracts — changing stage behavior means editing
a committed file, not an ad-hoc string in code.

## Running the workflow

```bash
python scripts/run_adjudication_workflow.py \
  --labels-path output/labels/results.json \
  --output-path output/adjudication/results.json \
  --trace-path output/adjudication/trace.json \
  --escalation-path output/adjudication/escalations.jsonl \
  --provider local
```

Inspect:

- the adjudication results
- the workflow trace
- the escalation queue for cases routed to `needs_human_review`

Committed examples:

- [`artifacts/latest/adjudication_result_example.json`](../artifacts/latest/adjudication_result_example.json)
- [`artifacts/latest/adjudication_trace_example.json`](../artifacts/latest/adjudication_trace_example.json)
- [`artifacts/latest/adjudication_escalation_example.jsonl`](../artifacts/latest/adjudication_escalation_example.jsonl)
