from __future__ import annotations

from pydantic import BaseModel


class SignalsPayload(BaseModel):
    redness_ratio: float
    texture_score: float
    lesion_extent: float


class ModelPayload(BaseModel):
    raw_probability: float
    calibrated_probability: float
    model_name: str
    model_version: str


class DecisionPayload(BaseModel):
    bucket: str
    reasons: list[str]
    threshold_used: float


class RegionPayload(BaseModel):
    x0: int
    y0: int
    x1: int
    y1: int
    coverage: float
    image_width: int
    image_height: int


class AnalyzeResponse(BaseModel):
    inference_id: int
    request_id: str
    subject: str | None
    latency_ms: int
    signals: SignalsPayload
    region: RegionPayload
    model: ModelPayload
    decision: DecisionPayload


class InferenceRecordPayload(AnalyzeResponse):
    pass


class ExampleCasePayload(BaseModel):
    case_id: str
    label: str
    description: str
    image_url: str
