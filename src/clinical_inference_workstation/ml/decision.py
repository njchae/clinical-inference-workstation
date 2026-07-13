from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from clinical_inference_workstation.config import load_decision_rules
from clinical_inference_workstation.ml.features import VisualSignals


@dataclass(frozen=True)
class TriageDecision:
    bucket: str
    reasons: list[str]
    threshold_used: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def infer_probability_from_signals(signals: VisualSignals) -> float:
    logit = (
        signals.redness_ratio * 4.5
        + signals.texture_score * 3.2
        + signals.lesion_extent * 2.5
        - 1.8
    )
    probability = 1.0 / (1.0 + math.exp(-logit))
    return round(probability, 4)


def decide_triage(
    signals: VisualSignals,
    calibrated_probability: float,
) -> TriageDecision:
    rules = load_decision_rules()
    signal_thresholds = rules["signals"]
    model_thresholds = rules["model"]

    reasons: list[str] = []
    if signals.redness_ratio >= signal_thresholds["redness_alert"]:
        reasons.append("redness_alert")
    if signals.texture_score >= signal_thresholds["texture_alert"]:
        reasons.append("texture_alert")
    if calibrated_probability >= model_thresholds["review_threshold"]:
        reasons.append("model_probability")

    urgent = (
        signals.redness_ratio >= signal_thresholds["redness_alert"] + 0.12
        and calibrated_probability >= model_thresholds["urgent_threshold"]
    )
    if urgent:
        return TriageDecision(
            bucket="urgent_review",
            reasons=reasons or ["model_probability"],
            threshold_used=model_thresholds["urgent_threshold"],
        )

    if reasons:
        return TriageDecision(
            bucket="review_soon",
            reasons=reasons,
            threshold_used=model_thresholds["review_threshold"],
        )

    return TriageDecision(
        bucket="routine_monitor",
        reasons=["below_review_threshold"],
        threshold_used=model_thresholds["review_threshold"],
    )

