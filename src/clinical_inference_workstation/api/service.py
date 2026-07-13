from __future__ import annotations

import json
import time
from io import BytesIO

from PIL import Image

from clinical_inference_workstation.api.audit import load_inference_record, next_inference_id, write_inference_record
from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.ml.bundle import load_model_bundle
from clinical_inference_workstation.ml.decision import decide_triage, infer_probability_from_signals
from clinical_inference_workstation.ml.features import extract_visual_signals, locate_signal_region


ARTIFACT_DIR = ROOT_DIR / "artifacts" / "latest"
EXAMPLES_FILE = ROOT_DIR / "web" / "samples" / "examples.json"


def analyze_image_bytes(content: bytes, *, request_id: str, subject: str | None) -> dict[str, object]:
    started = time.perf_counter()
    image = Image.open(BytesIO(content))
    signals = extract_visual_signals(image)
    region = locate_signal_region(image)
    if ARTIFACT_DIR.exists():
        probability = load_model_bundle(ARTIFACT_DIR).predict_probability(image)
        model_name = "tiny_linear_model"
        model_version = "artifact_bundle_v1"
    else:
        probability = infer_probability_from_signals(signals)
        model_name = "signal_fallback_heuristic"
        model_version = "inline_v1"
    decision = decide_triage(signals=signals, calibrated_probability=probability)
    payload = {
        "inference_id": next_inference_id(),
        "request_id": request_id,
        "subject": subject,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "signals": signals.as_dict(),
        "region": {
            **region.as_dict(),
            "image_width": image.size[0],
            "image_height": image.size[1],
        },
        "model": {
            "raw_probability": probability,
            "calibrated_probability": probability,
            "model_name": model_name,
            "model_version": model_version,
        },
        "decision": decision.as_dict(),
    }
    write_inference_record(payload)
    return payload


def get_inference_record(inference_id: int) -> dict[str, object] | None:
    return load_inference_record(inference_id)


def load_examples() -> list[dict[str, str]]:
    if not EXAMPLES_FILE.exists():
        return []
    return json.loads(EXAMPLES_FILE.read_text(encoding="utf-8"))
