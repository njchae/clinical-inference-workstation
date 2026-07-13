from clinical_inference_workstation.ml.decision import decide_triage
from clinical_inference_workstation.ml.features import VisualSignals


def test_should_return_urgent_when_redness_and_model_probability_are_high() -> None:
    signals = VisualSignals(redness_ratio=0.41, texture_score=0.06, lesion_extent=0.38)

    result = decide_triage(signals=signals, calibrated_probability=0.81)

    assert result.bucket == "urgent_review"
    assert "model_probability" in result.reasons


def test_should_return_routine_when_signals_remain_below_review_thresholds() -> None:
    signals = VisualSignals(redness_ratio=0.07, texture_score=0.01, lesion_extent=0.09)

    result = decide_triage(signals=signals, calibrated_probability=0.19)

    assert result.bucket == "routine_monitor"

