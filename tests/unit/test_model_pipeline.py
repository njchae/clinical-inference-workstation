import json

from clinical_inference_workstation.ml.pipeline import run_training_pipeline


def test_should_write_public_artifacts_after_training_pipeline(tmp_path) -> None:
    output_dir = tmp_path / "artifacts"

    report = run_training_pipeline(output_dir=output_dir, dataset_size=60, image_size=48)

    assert report.metrics["sensitivity"] >= 0.7
    assert (output_dir / "metrics.json").exists()
    assert (output_dir / "thresholds.json").exists()
    assert (output_dir / "calibration.json").exists()
    assert (output_dir / "model.json").exists()
    assert (output_dir / "MODEL_CARD.md").exists()

    thresholds = json.loads((output_dir / "thresholds.json").read_text(encoding="utf-8"))
    assert 0.0 <= thresholds["review_threshold"] <= 1.0


def test_should_support_compact_cnn_family_and_write_comparison_report(tmp_path) -> None:
    output_dir = tmp_path / "cnn-artifacts"

    report = run_training_pipeline(
        output_dir=output_dir,
        dataset_size=60,
        image_size=48,
        model_family="compact_cnn",
    )

    model_payload = json.loads((output_dir / "model.json").read_text(encoding="utf-8"))
    comparison = json.loads((output_dir / "comparison.json").read_text(encoding="utf-8"))

    assert report.model_family == "compact_cnn"
    assert model_payload["model_family"] == "compact_cnn"
    assert 0.0 <= report.metrics["accuracy"] <= 1.0
    assert "baseline_linear" in comparison["available_model_families"]
    assert "compact_cnn" in comparison["available_model_families"]
