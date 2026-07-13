from __future__ import annotations

import base64
import hashlib
import hmac
import json
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from clinical_inference_workstation.api.app import create_app


def _build_sample_image_bytes() -> bytes:
    image = Image.new("RGB", (96, 96), (220, 220, 220))
    draw = ImageDraw.Draw(image)
    draw.ellipse((18, 18, 78, 78), fill=(232, 88, 88))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _encode_segment(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _issue_token(secret: str, *, sub: str = "demo-user") -> str:
    header = _encode_segment({"alg": "HS256", "typ": "JWT"})
    claims = _encode_segment(
        {
            "sub": sub,
            "iss": "clinical-inference-workstation",
            "aud": "clinical-inference-api",
        }
    )
    signing_input = f"{header}.{claims}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{header}.{claims}.{signature_encoded}"


def test_analyze_should_require_bearer_token_when_auth_enabled(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("STW_AUTH_MODE", "jwt")
    monkeypatch.setenv("STW_JWT_SECRET", "topsecret")
    monkeypatch.setenv("STW_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    client = TestClient(create_app())

    response = client.post(
        "/v1/analyze",
        files={"image": ("sample.png", _build_sample_image_bytes(), "image/png")},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_analyze_should_return_request_metadata_and_persist_audit_record(monkeypatch, tmp_path) -> None:
    secret = "topsecret"
    audit_log_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("STW_AUTH_MODE", "jwt")
    monkeypatch.setenv("STW_JWT_SECRET", secret)
    monkeypatch.setenv("STW_AUDIT_LOG_PATH", str(audit_log_path))
    client = TestClient(create_app())
    token = _issue_token(secret)

    response = client.post(
        "/v1/analyze",
        files={"image": ("sample.png", _build_sample_image_bytes(), "image/png")},
        headers={"Authorization": f"Bearer {token}"},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["request_id"]
    assert payload["model"]["model_name"]
    assert payload["model"]["model_version"]
    assert payload["latency_ms"] >= 0
    assert payload["decision"]["threshold_used"] >= 0.0

    lines = audit_log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["request_id"] == payload["request_id"]
    assert record["subject"] == "demo-user"
    assert record["decision"]["bucket"] == payload["decision"]["bucket"]


def test_get_inference_should_return_persisted_record(monkeypatch, tmp_path) -> None:
    secret = "topsecret"
    monkeypatch.setenv("STW_AUTH_MODE", "jwt")
    monkeypatch.setenv("STW_JWT_SECRET", secret)
    monkeypatch.setenv("STW_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    client = TestClient(create_app())
    token = _issue_token(secret)

    create_response = client.post(
        "/v1/analyze",
        files={"image": ("sample.png", _build_sample_image_bytes(), "image/png")},
        headers={"Authorization": f"Bearer {token}"},
    )
    inference_id = create_response.json()["inference_id"]

    get_response = client.get(
        f"/v1/inferences/{inference_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    payload = get_response.json()

    assert get_response.status_code == 200
    assert payload["inference_id"] == inference_id
    assert payload["request_id"] == create_response.json()["request_id"]
    assert payload["model"]["model_name"] == create_response.json()["model"]["model_name"]
