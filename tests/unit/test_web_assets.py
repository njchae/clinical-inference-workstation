from pathlib import Path


def test_workstation_index_should_describe_operator_flow() -> None:
    index_path = Path("web/index.html")

    contents = index_path.read_text(encoding="utf-8")

    assert "Synthetic Triage Workstation" in contents
    assert "Sample cases" in contents
    assert "Decision summary" in contents


def test_workstation_index_should_include_case_view_overlay_surface() -> None:
    contents = Path("web/index.html").read_text(encoding="utf-8")

    assert "Case view" in contents
    assert "case-canvas" in contents


def test_workstation_app_should_draw_region_overlay_and_threshold_marker() -> None:
    contents = Path("web/app.js").read_text(encoding="utf-8")

    assert "region" in contents
    assert "threshold_used" in contents
    assert "case-canvas" in contents
    assert "signal-bars" in contents
