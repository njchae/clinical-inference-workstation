from pathlib import Path


def test_workstation_index_should_describe_operator_flow() -> None:
    index_path = Path("web/index.html")

    contents = index_path.read_text(encoding="utf-8")

    assert "Inference Review Workstation" in contents
    assert "Recorded inference cases" in contents
    assert "Review note" in contents


def test_workstation_index_should_include_recorded_case_review_surface() -> None:
    contents = Path("web/index.html").read_text(encoding="utf-8")

    assert "Field of view" in contents
    assert "case-canvas" in contents


def test_workstation_app_should_render_saved_pipeline_outputs_without_live_upload() -> None:
    contents = Path("web/app.js").read_text(encoding="utf-8")

    assert "public-cases.json" in contents
    assert "roi" in contents
    assert "detector_disagreement" in contents
    assert "case-canvas" in contents
    assert 'fetch("/v1/analyze"' not in contents
    assert "upload-input" not in contents
