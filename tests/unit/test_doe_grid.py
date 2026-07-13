from clinical_inference_workstation.doe.grid import build_metric_grid, read_doe_results

ROWS = [
    {"temperature": 0.8, "threshold": 0.30, "specificity": 0.77, "sensitivity": 1.0, "meets_sensitivity_target": True},
    {"temperature": 0.8, "threshold": 0.45, "specificity": 1.00, "sensitivity": 1.0, "meets_sensitivity_target": True},
    {"temperature": 1.0, "threshold": 0.30, "specificity": 0.60, "sensitivity": 1.0, "meets_sensitivity_target": True},
    {"temperature": 1.0, "threshold": 0.45, "specificity": 0.90, "sensitivity": 0.5, "meets_sensitivity_target": False},
]


def test_should_pivot_rows_into_temperature_by_threshold_grid():
    grid = build_metric_grid(ROWS, metric="specificity")

    assert grid.temperatures == [0.8, 1.0]
    assert grid.thresholds == [0.30, 0.45]
    # z is indexed [threshold_row][temperature_col]
    assert grid.z[1][0] == 1.00
    assert grid.z[0][1] == 0.60


def test_should_pick_best_cell_among_target_meeting_rows():
    grid = build_metric_grid(ROWS, metric="specificity")

    assert grid.best is not None
    assert grid.best.temperature == 0.8
    assert grid.best.threshold == 0.45
    assert grid.best.value == 1.00


def test_should_report_no_best_when_no_row_meets_target():
    rows = [
        {"temperature": 1.0, "threshold": 0.45, "specificity": 0.90, "sensitivity": 0.5, "meets_sensitivity_target": False},
    ]

    grid = build_metric_grid(rows, metric="specificity")

    assert grid.best is None


def test_should_read_and_type_rows_from_csv(tmp_path):
    csv_path = tmp_path / "doe_results.csv"
    csv_path.write_text(
        "temperature,threshold,sensitivity,specificity,accuracy,meets_sensitivity_target,objective\n"
        "0.8,0.3,1.0,0.7692,0.875,True,0.7692\n"
        "1.0,0.45,0.5,0.9,0.7,False,\n",
        encoding="utf-8",
    )

    rows = read_doe_results(csv_path)

    assert rows[0]["temperature"] == 0.8
    assert rows[0]["meets_sensitivity_target"] is True
    assert rows[1]["meets_sensitivity_target"] is False
    assert rows[1]["objective"] is None
