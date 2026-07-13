"""Run a DOE sweep over ``(temperature, threshold)`` cells and record outcomes.

Each cell reuses the exact primitives the training pipeline already uses —
``apply_temperature`` (temperature scaling) and ``binary_metrics``
(sensitivity/specificity/accuracy at a threshold) — so a sweep is a faithful
generalization of the per-pathway calibration + threshold-selection step, not a
separate evaluation path.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

from clinical_inference_workstation.doe.matrix import (
    build_fractional_factorial,
    build_full_factorial,
)
from clinical_inference_workstation.ml.pipeline import apply_temperature, binary_metrics


@dataclass(frozen=True)
class SweepCell:
    params: dict[str, float]
    sensitivity: float
    specificity: float
    accuracy: float
    meets_target: bool
    objective: float | None


@dataclass(frozen=True)
class SweepResult:
    cells: list[SweepCell]
    best: SweepCell | None
    target_sensitivity: float
    factors: dict[str, list] = field(default_factory=dict)


def _score_cell(
    probabilities: list[float],
    labels: list[int],
    params: dict[str, float],
    target_sensitivity: float,
) -> SweepCell:
    temperature = float(params.get("temperature", 1.0))
    threshold = float(params["threshold"])
    calibrated = [apply_temperature(probability, temperature) for probability in probabilities]
    metrics = binary_metrics(calibrated, labels, threshold)
    meets_target = metrics["sensitivity"] >= target_sensitivity
    return SweepCell(
        params=params,
        sensitivity=metrics["sensitivity"],
        specificity=metrics["specificity"],
        accuracy=metrics["accuracy"],
        meets_target=meets_target,
        # Objective mirrors the pipeline's threshold rule: maximize specificity
        # among configurations that clear the sensitivity floor.
        objective=metrics["specificity"] if meets_target else None,
    )


def _select_best(cells: list[SweepCell]) -> SweepCell | None:
    qualifying = [cell for cell in cells if cell.meets_target]
    if not qualifying:
        return None
    # Highest specificity wins; ties break toward the lower threshold (more
    # conservative operating point), matching _find_threshold's preference order.
    return max(
        qualifying,
        key=lambda cell: (cell.specificity, -float(cell.params["threshold"])),
    )


def run_sweep(
    probabilities: list[float],
    labels: list[int],
    factors: dict[str, list],
    target_sensitivity: float,
    design: str = "full_factorial",
    fraction: int | None = None,
) -> SweepResult:
    """Evaluate every cell in the design and pick the best target-meeting cell."""
    if design == "fractional_factorial":
        cells_params = build_fractional_factorial(factors, fraction or 2)
    else:
        cells_params = build_full_factorial(factors)

    cells = [_score_cell(probabilities, labels, params, target_sensitivity) for params in cells_params]
    return SweepResult(
        cells=cells,
        best=_select_best(cells),
        target_sensitivity=target_sensitivity,
        factors=factors,
    )


def write_sweep_artifacts(result: SweepResult, output_dir: Path) -> dict[str, str]:
    """Write ``doe_results.csv`` (one row per cell) and ``doe_summary.json``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "doe_results.csv"
    summary_path = output_dir / "doe_summary.json"

    factor_columns = list(result.factors)
    fieldnames = [
        *factor_columns,
        "sensitivity",
        "specificity",
        "accuracy",
        "meets_sensitivity_target",
        "objective",
    ]
    with results_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for cell in result.cells:
            row: dict[str, object] = {name: cell.params.get(name) for name in factor_columns}
            row.update(
                {
                    "sensitivity": cell.sensitivity,
                    "specificity": cell.specificity,
                    "accuracy": cell.accuracy,
                    "meets_sensitivity_target": cell.meets_target,
                    "objective": cell.objective if cell.objective is not None else "",
                }
            )
            writer.writerow(row)

    summary: dict[str, object] = {
        "n_cells": len(result.cells),
        "factors": result.factors,
        "target_sensitivity": result.target_sensitivity,
        "best": None,
    }
    if result.best is not None:
        summary["best"] = {
            "params": result.best.params,
            "sensitivity": result.best.sensitivity,
            "specificity": result.best.specificity,
            "accuracy": result.best.accuracy,
        }

    committed = _committed_configuration(output_dir)
    if committed:
        summary["committed_configuration"] = committed

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"results_csv": str(results_path), "summary_json": str(summary_path)}


def _committed_configuration(output_dir: Path) -> dict[str, float] | None:
    """Read the pipeline's committed temperature/threshold, if present, for comparison."""
    calibration_path = output_dir / "calibration.json"
    thresholds_path = output_dir / "thresholds.json"
    if not calibration_path.exists() or not thresholds_path.exists():
        return None
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    thresholds = json.loads(thresholds_path.read_text(encoding="utf-8"))
    return {
        "temperature": calibration.get("temperature"),
        "review_threshold": thresholds.get("review_threshold"),
    }
