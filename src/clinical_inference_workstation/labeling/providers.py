from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from PIL import Image

from clinical_inference_workstation.labeling.schemas import LabelResult, LabelSignals


class LabelProvider(Protocol):
    provider_name: str

    def label_image(self, image_path: Path) -> LabelResult:
        ...


class LocalHeuristicLabelProvider:
    provider_name = "local"

    def label_image(self, image_path: Path) -> LabelResult:
        image = Image.open(image_path).convert("RGB")
        pixels = list(image.getdata())
        total = max(len(pixels), 1)
        redness_ratio = sum(1 for r, g, b in pixels if r > g + 20 and r > b + 20) / total
        brightness = sum((r + g + b) / 3.0 for r, g, b in pixels) / total
        texture_present = brightness < 210
        lesion_visible = redness_ratio >= 0.08 or texture_present
        confidence = 0.92 if redness_ratio >= 0.08 else 0.64
        review_required = confidence < 0.8
        return LabelResult(
            case_id=image_path.stem,
            image_path=str(image_path),
            provider=self.provider_name,
            confidence=confidence,
            rationale="Local heuristic provider estimated visual feature presence from synthetic image colors.",
            image_quality="good",
            review_required=review_required,
            signals=LabelSignals(
                redness_present=redness_ratio >= 0.08,
                texture_present=texture_present,
                lesion_visible=lesion_visible,
            ),
        )


class ProviderConfigurationError(RuntimeError):
    """Raised when a remote provider is not configured."""


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def label_image(self, image_path: Path) -> LabelResult:
        del image_path
        raise ProviderConfigurationError(
            "OpenAI provider adapter is present, but live API calling is intentionally not exercised in the public demo. "
            "Use the local provider in CI or extend this adapter with your endpoint configuration."
        )


class AnthropicProvider:
    provider_name = "anthropic"

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def label_image(self, image_path: Path) -> LabelResult:
        del image_path
        raise ProviderConfigurationError(
            "Anthropic provider adapter is present, but live API calling is intentionally not exercised in the public demo. "
            "Use the local provider in CI or extend this adapter with your endpoint configuration."
        )


def build_provider(provider_name: str) -> LabelProvider:
    normalized = provider_name.strip().lower()
    if normalized == "local":
        return LocalHeuristicLabelProvider()
    if normalized == "openai":
        return OpenAIProvider()
    if normalized == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unsupported provider '{provider_name}'")
