from clinical_inference_workstation.doe.sweep import run_sweep


def test_should_record_one_result_cell_per_grid_cell():
    factors = {"temperature": [1.0, 2.0], "threshold": [0.4, 0.6]}

    result = run_sweep(
        probabilities=[0.9, 0.6, 0.4, 0.1],
        labels=[1, 1, 0, 0],
        factors=factors,
        target_sensitivity=0.7,
    )

    assert len(result.cells) == 4


def test_should_select_target_meeting_cell_with_best_specificity():
    # threshold 0.5 -> preds [1,1,0,0]: sensitivity 1.0, specificity 1.0 (meets target)
    # threshold 0.65 -> preds [1,0,0,0]: sensitivity 0.5 (misses target)
    factors = {"temperature": [1.0], "threshold": [0.5, 0.65]}

    result = run_sweep(
        probabilities=[0.9, 0.6, 0.4, 0.1],
        labels=[1, 1, 0, 0],
        factors=factors,
        target_sensitivity=0.7,
    )

    assert result.best is not None
    assert result.best.params == {"temperature": 1.0, "threshold": 0.5}
    assert result.best.specificity == 1.0


def test_should_report_no_best_when_no_cell_meets_target():
    factors = {"temperature": [1.0], "threshold": [0.65]}

    result = run_sweep(
        probabilities=[0.9, 0.6, 0.4, 0.1],
        labels=[1, 1, 0, 0],
        factors=factors,
        target_sensitivity=1.0,
    )

    assert result.best is None
