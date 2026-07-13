"""Render a shareable Markdown report from committed evaluation artifacts.

Pulls together the artifacts the pipeline and DOE sweep already emit
(``metrics.json``, ``calibration.json``, ``thresholds.json``, ``comparison.json``,
``doe_summary.json``) into a single report so a reviewer can compare
configurations without re-running anything. Missing artifacts are skipped.
"""

from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _metrics_section(metrics: dict) -> list[str]:
    lines = ["## Held-out Metrics", ""]
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    for label, key in (("Sensitivity", "sensitivity"), ("Specificity", "specificity"), ("Accuracy", "accuracy")):
        if key in metrics:
            lines.append(f"| {label} | {metrics[key]:.4f} |")
    lines.append("")
    return lines


def _calibration_section(calibration: dict | None, thresholds: dict | None) -> list[str]:
    if not calibration and not thresholds:
        return []
    lines = ["## Calibration & Threshold", ""]
    if calibration and "temperature" in calibration:
        lines.append(f"- Calibration temperature: `{calibration['temperature']}`")
    if thresholds and "review_threshold" in thresholds:
        lines.append(f"- Review threshold: `{thresholds['review_threshold']}`")
    lines.append("")
    return lines


def _comparison_section(comparison: dict | None) -> list[str]:
    if not comparison:
        return []
    lines = ["## Model-family Comparison", ""]
    trained = comparison.get("trained_model_family")
    if trained:
        lines.append(f"- Trained family: `{trained}`")
    available = comparison.get("available_model_families")
    if available:
        lines.append(f"- Available families: {', '.join(f'`{name}`' for name in available)}")
    lines.append("")
    return lines


def _doe_section(summary: dict | None) -> list[str]:
    if not summary:
        return []
    lines = ["## Best Swept Configuration", ""]
    lines.append(f"- Cells evaluated: {summary.get('n_cells', 0)}")
    lines.append(f"- Sensitivity target: {summary.get('target_sensitivity')}")
    best = summary.get("best")
    if best:
        params = ", ".join(f"{key}={value}" for key, value in best.get("params", {}).items())
        lines.append(f"- Best cell: {params}")
        lines.append(
            f"- At best cell — Sensitivity {best.get('sensitivity'):.4f}, "
            f"Specificity {best.get('specificity'):.4f}, Accuracy {best.get('accuracy'):.4f}"
        )
    else:
        lines.append("- No swept cell met the sensitivity target.")
    committed = summary.get("committed_configuration")
    if committed:
        lines.append(
            f"- Committed pipeline configuration: temperature "
            f"`{committed.get('temperature')}`, review threshold `{committed.get('review_threshold')}`"
        )
    lines.append("")
    return lines


def render_markdown_report(artifact_dir: Path) -> str:
    """Return a Markdown report string assembled from artifacts in ``artifact_dir``."""
    artifact_dir = Path(artifact_dir)
    metrics = _load_json(artifact_dir / "metrics.json") or {}
    calibration = _load_json(artifact_dir / "calibration.json")
    thresholds = _load_json(artifact_dir / "thresholds.json")
    comparison = _load_json(artifact_dir / "comparison.json")
    doe_summary = _load_json(artifact_dir / "doe_summary.json")

    lines = [
        "# Algorithm Configuration Report",
        "",
        "Generated from committed evaluation artifacts. Synthetic demo data — "
        "interpret as pipeline validation, not clinical performance.",
        "",
    ]
    lines += _metrics_section(metrics)
    lines += _calibration_section(calibration, thresholds)
    lines += _comparison_section(comparison)
    lines += _doe_section(doe_summary)
    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(artifact_dir: Path, output_path: Path) -> Path:
    """Render the report and write it to ``output_path``."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(artifact_dir), encoding="utf-8")
    return output_path
