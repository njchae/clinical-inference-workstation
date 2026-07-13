import json

from clinical_inference_workstation.reporting import render_markdown_report


def _seed_artifacts(artifact_dir):
    (artifact_dir / "metrics.json").write_text(
        json.dumps({"sensitivity": 0.90, "specificity": 0.85, "accuracy": 0.88})
    )
    (artifact_dir / "calibration.json").write_text(json.dumps({"temperature": 1.2}))
    (artifact_dir / "thresholds.json").write_text(json.dumps({"review_threshold": 0.45}))
    (artifact_dir / "doe_summary.json").write_text(
        json.dumps(
            {
                "n_cells": 25,
                "target_sensitivity": 0.7,
                "best": {
                    "params": {"temperature": 1.2, "threshold": 0.45},
                    "sensitivity": 0.90,
                    "specificity": 0.85,
                    "accuracy": 0.88,
                },
            }
        )
    )


def test_should_render_report_with_metrics_and_best_config(tmp_path):
    _seed_artifacts(tmp_path)

    report = render_markdown_report(tmp_path)

    assert "Best Swept Configuration" in report
    assert "Sensitivity" in report
    assert "0.85" in report


def test_should_render_report_without_doe_summary(tmp_path):
    (tmp_path / "metrics.json").write_text(
        json.dumps({"sensitivity": 0.90, "specificity": 0.85, "accuracy": 0.88})
    )

    report = render_markdown_report(tmp_path)

    assert "Sensitivity" in report
