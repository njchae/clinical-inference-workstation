from __future__ import annotations

import base64
import hashlib
import hmac
import json

from fastapi import Header, HTTPException, status

from clinical_inference_workstation.config import load_runtime_settings


def _decode_segment(value: str) -> dict[str, object]:
    padding = "=" * (-len(value) % 4)
    decoded = base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))
    return json.loads(decoded.decode("utf-8"))


def _validate_signature(header_segment: str, payload_segment: str, signature_segment: str, secret: str) -> None:
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual = base64.urlsafe_b64decode(f"{signature_segment}{'=' * (-len(signature_segment) % 4)}".encode("ascii"))
    if not hmac.compare_digest(expected, actual):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")


def require_subject(authorization: str | None = Header(default=None)) -> str | None:
    settings = load_runtime_settings()
    if settings.auth_mode != "jwt":
        return None
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    if not settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT secret is not configured")

    token = authorization.removeprefix("Bearer ").strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")

    header, payload, signature = parts
    header_payload = _decode_segment(header)
    if header_payload.get("alg") != "HS256":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported bearer token")
    _validate_signature(header, payload, signature, settings.jwt_secret)
    claims = _decode_segment(payload)
    if claims.get("iss") != settings.jwt_issuer or claims.get("aud") != settings.jwt_audience:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return subject
