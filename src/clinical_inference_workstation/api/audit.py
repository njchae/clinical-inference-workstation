from __future__ import annotations

import json
from pathlib import Path

from clinical_inference_workstation.config import load_runtime_settings


def _log_path() -> Path:
    path = load_runtime_settings().audit_log_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def next_inference_id() -> int:
    path = _log_path()
    if not path.exists():
        return 1
    return len(path.read_text(encoding="utf-8").splitlines()) + 1


def write_inference_record(record: dict[str, object]) -> None:
    path = _log_path()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def load_inference_record(inference_id: int) -> dict[str, object] | None:
    path = _log_path()
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get("inference_id") == inference_id:
            return payload
    return None
