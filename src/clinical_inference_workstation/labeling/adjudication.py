from __future__ import annotations

import json
from pathlib import Path

from clinical_inference_workstation.labeling.adjudication_providers import (
    AdjudicationProvider,
    build_adjudication_provider,
)
from clinical_inference_workstation.labeling.schemas import (
    AdjudicationResult,
    AdjudicationRunTrace,
    AdjudicationWorkflowReport,
    LabelResult,
)


def _load_labels(labels_path: Path) -> list[LabelResult]:
    payload = json.loads(labels_path.read_text(encoding="utf-8"))
    return [LabelResult.model_validate(item) for item in payload]


def run_adjudication_workflow(
    *,
    labels_path: Path,
    output_path: Path,
    trace_path: Path,
    escalation_path: Path,
    provider_name: str = "local",
    provider: AdjudicationProvider | None = None,
) -> AdjudicationWorkflowReport:
    labels = _load_labels(labels_path)
    adjudication_provider = provider or build_adjudication_provider(provider_name)
    results = [adjudication_provider.run_case(label) for label in labels]
    validated_results = [AdjudicationResult.model_validate(result) for result in results]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([item.model_dump() for item in validated_results], indent=2),
        encoding="utf-8",
    )

    trace = AdjudicationRunTrace(provider=adjudication_provider.provider_name, runs=validated_results)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(trace.model_dump(), indent=2), encoding="utf-8")

    escalation_rows = [item for item in validated_results if item.review_required]
    escalation_path.parent.mkdir(parents=True, exist_ok=True)
    escalation_path.write_text(
        "\n".join(json.dumps(item.model_dump()) for item in escalation_rows),
        encoding="utf-8",
    )

    return AdjudicationWorkflowReport(
        processed_count=len(validated_results),
        escalation_count=len(escalation_rows),
        provider_name=adjudication_provider.provider_name,
    )
