from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Request

from clinical_inference_workstation.api.auth import require_subject
from clinical_inference_workstation.api.schemas import AnalyzeResponse, ExampleCasePayload, InferenceRecordPayload
from clinical_inference_workstation.api.service import analyze_image_bytes, get_inference_record, load_examples
from clinical_inference_workstation.config import load_runtime_settings


router = APIRouter()


@router.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/model-info", tags=["Metadata"])
async def model_info() -> dict[str, str]:
    return {
        "model_family": "hybrid_rules_plus_tiny_linear_model",
        "data_mode": "synthetic_only",
        "auth_mode": load_runtime_settings().auth_mode,
    }


@router.get("/examples", response_model=list[ExampleCasePayload], tags=["Examples"])
async def examples() -> list[dict[str, str]]:
    return load_examples()


@router.post("/v1/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze(
    request: Request,
    image: UploadFile = File(...),
    subject: str | None = Depends(require_subject),
) -> dict[str, object]:
    return analyze_image_bytes(
        await image.read(),
        request_id=request.state.request_id,
        subject=subject,
    )


@router.get("/v1/inferences/{inference_id}", response_model=InferenceRecordPayload, tags=["Analysis"])
async def inference_record(
    inference_id: int,
    subject: str | None = Depends(require_subject),
) -> dict[str, object]:
    del subject
    record = get_inference_record(inference_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Inference record not found")
    return record
