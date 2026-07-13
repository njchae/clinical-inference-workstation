# Labeling Methodology

## Purpose

The labeling workflow demonstrates how a public-safe project can expose:

- structured output schemas
- checkpointed batch processing
- low-confidence routing into manual review
- reviewed-label export back into model development

It does **not** claim that the labels are clinically valid.

## Providers

The repo includes provider adapters for:

- `local`
- `openai`
- `anthropic`

CI uses the local provider because it is deterministic and public-safe. The remote provider adapters exist to show interface shape and configuration boundaries without embedding live credentials or tenant-specific endpoints.

## Output contract

Each label result includes:

- `case_id`
- `image_path`
- `provider`
- `confidence`
- `rationale`
- `image_quality`
- `review_required`
- typed visual signals

The output is validated through Pydantic models before being written to disk.

## Review flow

1. Run `python scripts/label_images.py`.
2. Inspect the generated review queue JSONL file.
3. Mark accepted items with `review_status=accepted`.
4. Export accepted rows with `python scripts/export_reviewed_labels.py`.

This keeps the weak-label stage visibly separate from the reviewed-label stage.
