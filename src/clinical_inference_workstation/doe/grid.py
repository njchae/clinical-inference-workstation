"""Pivot DOE sweep results into a temperature x threshold grid for visualization.

Pure, dependency-light helpers (stdlib only) so they can be unit-tested without
Streamlit/Plotly and reused by the dashboard's DOE heatmap tab.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

_FLOAT_COLUMNS = ("temperature", "threshold", "sensitivity", "specificity", "accuracy", "objective")


@dataclass(frozen=True)
class BestCell:
    temperature: float
    threshold: float
    value: float


@dataclass(frozen=True)
class MetricGrid:
    temperatures: list[float]
    thresholds: list[float]
    z: list[list[float | None]]
    metric: str
    best: BestCell | None


def read_doe_results(csv_path: Path) -> list[dict]:
    """Read ``doe_results.csv`` and coerce column types (floats, bool, None)."""
    rows: list[dict] = []
    with Path(csv_path).open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row: dict = {}
            for key, value in raw.items():
                if key == "meets_sensitivity_target":
                    row[key] = str(value).strip().lower() == "true"
                elif key in _FLOAT_COLUMNS:
                    row[key] = float(value) if value not in (None, "") else None
                else:
                    row[key] = value
            rows.append(row)
    return rows


def build_metric_grid(rows: list[dict], metric: str = "specificity") -> MetricGrid:
    """Pivot rows into a grid where ``z[threshold_index][temperature_index]`` is the metric.

    ``best`` is the cell with the highest metric among rows that met the sensitivity
    target, or ``None`` when no cell qualified.
    """
    temperatures = sorted({row["temperature"] for row in rows})
    thresholds = sorted({row["threshold"] for row in rows})
    temp_index = {value: i for i, value in enumerate(temperatures)}
    thr_index = {value: i for i, value in enumerate(thresholds)}

    z: list[list[float | None]] = [[None for _ in temperatures] for _ in thresholds]
    for row in rows:
        z[thr_index[row["threshold"]]][temp_index[row["temperature"]]] = row.get(metric)

    best: BestCell | None = None
    for row in rows:
        if not row.get("meets_sensitivity_target"):
            continue
        value = row.get(metric)
        if value is None:
            continue
        if best is None or value > best.value:
            best = BestCell(temperature=row["temperature"], threshold=row["threshold"], value=value)

    return MetricGrid(temperatures=temperatures, thresholds=thresholds, z=z, metric=metric, best=best)
