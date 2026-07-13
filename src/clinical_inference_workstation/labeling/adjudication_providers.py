from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.labeling.schemas import (
    AdjudicationResult,
    AdjudicationStageResult,
    LabelResult,
)


class AdjudicationProvider(Protocol):
    provider_name: str

    def run_case(self, label: LabelResult) -> AdjudicationResult:
        ...


class AdjudicationProviderConfigurationError(RuntimeError):
    """Raised when a remote adjudication provider is not configured."""


def _load_prompt_template(name: str) -> str:
    return (ROOT_DIR / "configs" / "adjudication_prompts" / f"{name}.md").read_text(encoding="utf-8")


class LocalDeterministicAdjudicationProvider:
    provider_name = "local"

    def run_case(self, label: LabelResult) -> AdjudicationResult:
        workflow_run_id = f"adj-{uuid4().hex[:12]}"
        evidence_summary = {
            "weak_label_confidence": label.confidence,
            "initial_review_required": label.review_required,
            "image_quality": label.image_quality,
            "signal_flags": {
                "redness_present": label.signals.redness_present,
                "texture_present": label.signals.texture_present,
                "lesion_visible": label.signals.lesion_visible,
            },
        }
        stage_results = [
            AdjudicationStageResult(
                stage_name="evidence_collector",
                status="completed",
                allowed_tools=["label_record", "signal_summary", "policy_notes"],
                prompt_template=_load_prompt_template("evidence_collector"),
                output={
                    "summary": "Collected weak label, signal flags, and review posture for adjudication.",
                    "evidence": evidence_summary,
                },
            )
        ]

        signal_count = sum(
            [
                label.signals.redness_present,
                label.signals.texture_present,
                label.signals.lesion_visible,
            ]
        )
        evidence_strength = "strong" if label.confidence >= 0.85 and signal_count >= 2 else "mixed"
        recommended_decision = "accept" if evidence_strength == "strong" else "needs_human_review"
        reviewer_confidence = 0.91 if recommended_decision == "accept" else 0.62
        stage_results.append(
            AdjudicationStageResult(
                stage_name="label_reviewer",
                status="completed",
                allowed_tools=["evidence_bundle"],
                prompt_template=_load_prompt_template("label_reviewer"),
                output={
                    "recommended_decision": recommended_decision,
                    "evidence_strength": evidence_strength,
                    "rationale": label.rationale,
                    "confidence": reviewer_confidence,
                },
            )
        )

        insufficient_evidence = label.confidence < 0.3 or label.image_quality == "poor"
        safety_flags: list[str] = []
        if label.image_quality == "poor":
            safety_flags.append("image_quality_insufficient_for_review")
        if label.confidence < 0.3:
            safety_flags.append("confidence_too_low_to_adjudicate")
        if not insufficient_evidence and label.image_quality != "good":
            safety_flags.append("image_quality_below_expected")
        if not insufficient_evidence and recommended_decision == "accept" and label.confidence < 0.85:
            safety_flags.append("acceptance_confidence_too_low")
        stage_results.append(
            AdjudicationStageResult(
                stage_name="safety_checker",
                status="completed",
                allowed_tools=["review_policy", "evidence_bundle"],
                prompt_template=_load_prompt_template("safety_checker"),
                output={
                    "safe_to_accept": not safety_flags and recommended_decision == "accept",
                    "flags": safety_flags,
                    "policy_note": "Reject cases with insufficient evidence rather than routing them to a human review queue that cannot resolve the underlying data problem.",
                },
            )
        )

        if insufficient_evidence:
            final_decision = "reject_for_insufficient_evidence"
            review_required = False
            review_reason = "insufficient_evidence_to_adjudicate"
            decision_confidence = 0.95
        elif recommended_decision == "accept" and not safety_flags:
            final_decision = "accept"
            review_required = False
            review_reason = "sufficient_structured_evidence"
            decision_confidence = 0.9
        else:
            final_decision = "needs_human_review"
            review_required = True
            review_reason = "weak_or_conflicting_evidence"
            decision_confidence = 0.63

        stage_results.append(
            AdjudicationStageResult(
                stage_name="review_router",
                status="completed",
                allowed_tools=["review_policy", "stage_results"],
                prompt_template=_load_prompt_template("review_router"),
                output={
                    "final_decision": final_decision,
                    "review_required": review_required,
                    "review_reason": review_reason,
                },
            )
        )

        return AdjudicationResult(
            workflow_run_id=workflow_run_id,
            case_id=label.case_id,
            provider=self.provider_name,
            stage_results=stage_results,
            final_decision=final_decision,
            decision_confidence=decision_confidence,
            review_required=review_required,
            review_reason=review_reason,
        )


class OpenAIAdjudicationProvider:
    provider_name = "openai"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def run_case(self, label: LabelResult) -> AdjudicationResult:
        del label
        raise AdjudicationProviderConfigurationError(
            "OpenAI adjudication adapter is present, but live API calling is intentionally not exercised in the public demo. "
            "Use the local provider in CI or extend this adapter with your endpoint configuration."
        )


class AnthropicAdjudicationProvider:
    provider_name = "anthropic"

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def run_case(self, label: LabelResult) -> AdjudicationResult:
        del label
        raise AdjudicationProviderConfigurationError(
            "Anthropic adjudication adapter is present, but live API calling is intentionally not exercised in the public demo. "
            "Use the local provider in CI or extend this adapter with your endpoint configuration."
        )


def build_adjudication_provider(provider_name: str) -> AdjudicationProvider:
    normalized = provider_name.strip().lower()
    if normalized == "local":
        return LocalDeterministicAdjudicationProvider()
    if normalized == "openai":
        return OpenAIAdjudicationProvider()
    if normalized == "anthropic":
        return AnthropicAdjudicationProvider()
    raise ValueError(f"Unsupported provider '{provider_name}'")
