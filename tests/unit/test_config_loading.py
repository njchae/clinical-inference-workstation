from clinical_inference_workstation.config import (
    load_decision_rules,
    load_synthetic_data_config,
    load_training_config,
)


def test_should_load_synthetic_data_config_with_named_sample_cases() -> None:
    config = load_synthetic_data_config()

    assert config["dataset"]["image_size"] > 0
    assert len(config["sample_cases"]) >= 3
    assert all(isinstance(case["seed"], int) for case in config["sample_cases"])
    assert all(case["label"] for case in config["sample_cases"])


def test_should_load_training_config_with_split_and_calibration_controls() -> None:
    config = load_training_config()

    assert config["splits"]["train_ratio"] == 0.6
    assert config["thresholding"]["target_sensitivity"] == 0.7
    assert config["calibration"]["temperature_min"] < config["calibration"]["temperature_max"]


def test_decision_rules_should_keep_thresholds_separate_from_training_config() -> None:
    rules = load_decision_rules()

    assert "model" in rules
    assert "review_threshold" in rules["model"]

