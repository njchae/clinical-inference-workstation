from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_inference_workstation.labeling.adjudication import (
    run_adjudication_workflow,
)
from clinical_inference_workstation.labeling.adjudication_providers import (
    AdjudicationProvider,
    build_adjudication_provider,
)
from clinical_inference_workstation.labeling.schemas import (
    AdjudicationResult,
    LabelResult,
)


def _write_labels(path: Path) -> None:
    path.write_text(
        json.dumps(
            [
                {
                    "case_id": "case_accept",
                    "image_path": "web/samples/case_accept.png",
                    "provider": "local",
                    "confidence": 0.93,
                    "rationale": "Strong redness and lesion signal.",
                    "image_quality": "good",
                    "review_required": False,
                    "review_status": "pending",
                    "signals": {
                        "redness_present": True,
                        "texture_present": True,
                        "lesion_visible": True,
                    },
                },
                {
                    "case_id": "case_escalate",
                    "image_path": "web/samples/case_escalate.png",
                    "provider": "local",
                    "confidence": 0.61,
                    "rationale": "Weak label confidence with mixed evidence.",
                    "image_quality": "good",
                    "review_required": True,
                    "review_status": "pending",
                    "signals": {
                        "redness_present": True,
                        "texture_present": False,
                        "lesion_visible": False,
                    },
                },
                {
                    "case_id": "case_reject",
                    "image_path": "web/samples/case_reject.png",
                    "provider": "local",
                    "confidence": 0.21,
                    "rationale": "Very low confidence; image quality too poor to adjudicate.",
                    "image_quality": "poor",
                    "review_required": True,
                    "review_status": "pending",
                    "signals": {
                        "redness_present": False,
                        "texture_present": False,
                        "lesion_visible": False,
                    },
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def test_adjudication_workflow_should_accept_strong_cases_and_escalate_weak_cases(tmp_path: Path) -> None:
    labels_path = tmp_path / "labels.json"
    output_path = tmp_path / "adjudication_results.json"
    trace_path = tmp_path / "adjudication_trace.json"
    escalation_path = tmp_path / "escalations.jsonl"
    _write_labels(labels_path)

    report = run_adjudication_workflow(
        labels_path=labels_path,
        output_path=output_path,
        trace_path=trace_path,
        escalation_path=escalation_path,
        provider_name="local",
    )

    assert report.processed_count == 3
    assert report.escalation_count == 1
    assert report.provider_name == "local"

    results = [AdjudicationResult.model_validate(item) for item in json.loads(output_path.read_text(encoding="utf-8"))]
    by_case_id = {item.case_id: item for item in results}

    assert by_case_id["case_accept"].final_decision == "accept"
    assert by_case_id["case_accept"].review_required is False
    assert by_case_id["case_accept"].stage_results[0].stage_name == "evidence_collector"
    assert by_case_id["case_accept"].stage_results[-1].stage_name == "review_router"

    assert by_case_id["case_escalate"].final_decision == "needs_human_review"
    assert by_case_id["case_escalate"].review_required is True
    assert by_case_id["case_escalate"].review_reason == "weak_or_conflicting_evidence"

    assert by_case_id["case_reject"].final_decision == "reject_for_insufficient_evidence"
    assert by_case_id["case_reject"].review_required is False
    assert by_case_id["case_reject"].review_reason == "insufficient_evidence_to_adjudicate"

    trace_payload = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace_payload["provider"] == "local"
    assert len(trace_payload["runs"]) == 3

    escalation_rows = [json.loads(line) for line in escalation_path.read_text(encoding="utf-8").splitlines()]
    assert len(escalation_rows) == 1
    assert escalation_rows[0]["case_id"] == "case_escalate"


class InvalidStructureProvider:
    provider_name = "broken"

    def run_case(self, label: LabelResult):  # type: ignore[no-untyped-def]
        del label
        return {
            "workflow_run_id": "broken-run",
            "case_id": "broken-case",
            "provider": "broken",
            "stage_results": [
                {
                    "stage_name": "evidence_collector",
                    "allowed_tools": ["label_record"],
                    "output": {"summary": "missing status field"},
                }
            ],
            "final_decision": "accept",
            "decision_confidence": 0.9,
            "review_required": False,
            "review_reason": "none",
        }


def test_adjudication_workflow_should_fail_when_provider_output_breaks_contract(tmp_path: Path) -> None:
    labels_path = tmp_path / "labels.json"
    _write_labels(labels_path)

    with pytest.raises(Exception):
        run_adjudication_workflow(
            labels_path=labels_path,
            output_path=tmp_path / "results.json",
            trace_path=tmp_path / "trace.json",
            escalation_path=tmp_path / "escalations.jsonl",
            provider=InvalidStructureProvider(),
        )


def test_adjudication_workflow_should_reject_cases_with_insufficient_evidence(tmp_path: Path) -> None:
    labels_path = tmp_path / "labels.json"
    labels_path.write_text(
        json.dumps(
            [
                {
                    "case_id": "case_poor_quality",
                    "image_path": "web/samples/case_poor.png",
                    "provider": "local",
                    "confidence": 0.21,
                    "rationale": "Image too degraded to assess.",
                    "image_quality": "poor",
                    "review_required": True,
                    "review_status": "pending",
                    "signals": {"redness_present": False, "texture_present": False, "lesion_visible": False},
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    report = run_adjudication_workflow(
        labels_path=labels_path,
        output_path=tmp_path / "results.json",
        trace_path=tmp_path / "trace.json",
        escalation_path=tmp_path / "escalations.jsonl",
        provider_name="local",
    )

    results = [AdjudicationResult.model_validate(item) for item in json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))]
    assert results[0].final_decision == "reject_for_insufficient_evidence"
    assert results[0].review_required is False
    assert results[0].review_reason == "insufficient_evidence_to_adjudicate"
    assert report.escalation_count == 0


def test_build_adjudication_provider_should_reject_unsupported_provider() -> None:
    with pytest.raises(ValueError):
        build_adjudication_provider("unsupported")


def test_adjudication_prompt_templates_should_be_present() -> None:
    prompts_dir = Path("configs/adjudication_prompts")
    names = sorted(path.name for path in prompts_dir.glob("*.md"))

    assert names == [
        "evidence_collector.md",
        "label_reviewer.md",
        "review_router.md",
        "safety_checker.md",
    ]
