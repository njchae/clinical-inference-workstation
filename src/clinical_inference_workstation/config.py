from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIGS_DIR = ROOT_DIR / "configs"


@dataclass(frozen=True)
class RuntimeSettings:
    auth_mode: str
    jwt_secret: str
    jwt_issuer: str
    jwt_audience: str
    audit_log_path: Path


def _load_yaml_config(file_name: str) -> dict:
    with (CONFIGS_DIR / file_name).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=1)
def load_decision_rules() -> dict:
    return _load_yaml_config("decision_rules.yaml")


@lru_cache(maxsize=1)
def load_synthetic_data_config() -> dict:
    return _load_yaml_config("synthetic_data.yaml")


@lru_cache(maxsize=1)
def load_training_config() -> dict:
    return _load_yaml_config("training.yaml")


@lru_cache(maxsize=1)
def load_doe_config() -> dict:
    return _load_yaml_config("doe/threshold_sweep.yaml")


def load_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        auth_mode=os.getenv("STW_AUTH_MODE", "disabled").strip().lower() or "disabled",
        jwt_secret=os.getenv("STW_JWT_SECRET", ""),
        jwt_issuer=os.getenv("STW_JWT_ISSUER", "clinical-inference-workstation"),
        jwt_audience=os.getenv("STW_JWT_AUDIENCE", "clinical-inference-api"),
        audit_log_path=Path(
            os.getenv(
                "STW_AUDIT_LOG_PATH",
                str(ROOT_DIR / "output" / "inference_audit.jsonl"),
            )
        ),
    )
