from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LabelSignals(BaseModel):
    redness_present: bool
    texture_present: bool
    lesion_visible: bool


class LabelResult(BaseModel):
    case_id: str
    image_path: str
    provider: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    image_quality: str
    review_required: bool
    review_status: str = "pending"
    signals: LabelSignals


class LabelingRunReport(BaseModel):
    processed_count: int
    resumed_from_checkpoint: bool
    review_queue_count: int


class AdjudicationStageResult(BaseModel):
    stage_name: Literal["evidence_collector", "label_reviewer", "safety_checker", "review_router"]
    status: Literal["completed"]
    allowed_tools: list[str]
    prompt_template: str
    output: dict[str, object]


class AdjudicationResult(BaseModel):
    workflow_run_id: str
    case_id: str
    provider: str
    stage_results: list[AdjudicationStageResult]
    final_decision: Literal["accept", "needs_human_review", "reject_for_insufficient_evidence"]
    decision_confidence: float = Field(ge=0.0, le=1.0)
    review_required: bool
    review_reason: str


class AdjudicationRunTrace(BaseModel):
    provider: str
    runs: list[AdjudicationResult]


class AdjudicationWorkflowReport(BaseModel):
    processed_count: int
    escalation_count: int
    provider_name: str
