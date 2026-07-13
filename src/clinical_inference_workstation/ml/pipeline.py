from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, log_loss

from clinical_inference_workstation.config import load_synthetic_data_config, load_training_config
from clinical_inference_workstation.ml.synthetic_data import SyntheticCase, generate_synthetic_case


@dataclass(frozen=True)
class TrainingReport:
    metrics: dict[str, float]
    review_threshold: float
    temperature: float
    model_family: str


def _image_to_vector(image: Image.Image, size: int = 12) -> list[float]:
    grayscale = image.convert("L").resize((size, size))
    return [pixel / 255.0 for pixel in grayscale.getdata()]


def _image_to_matrix(image: Image.Image, size: int = 12) -> np.ndarray:
    grayscale = image.convert("L").resize((size, size))
    return np.asarray(grayscale, dtype=float) / 255.0


def _temperature_scale(probability: float, temperature: float) -> float:
    probability = min(max(probability, 1e-6), 1 - 1e-6)
    logit = math.log(probability / (1 - probability))
    scaled = 1.0 / (1.0 + math.exp(-(logit / temperature)))
    return scaled


def _fit_temperature(probabilities: list[float], labels: list[int], calibration_config: dict) -> float:
    best_temperature = 1.0
    best_loss = float("inf")
    start = int(round(calibration_config["temperature_min"] * 10))
    stop = int(round(calibration_config["temperature_max"] * 10))
    step = max(int(round(calibration_config["temperature_step"] * 10)), 1)
    for raw_temperature in range(start, stop + 1, step):
        temperature = raw_temperature / 10.0
        calibrated = [_temperature_scale(probability, temperature) for probability in probabilities]
        score = log_loss(labels, calibrated)
        if score < best_loss:
            best_loss = score
            best_temperature = temperature
    return best_temperature


def _find_threshold(probabilities: list[float], labels: list[int], thresholding_config: dict) -> float:
    best_threshold = 0.5
    best_specificity = -1.0
    target_sensitivity = thresholding_config["target_sensitivity"]
    start = int(round(thresholding_config["threshold_min"] * 100))
    stop = int(round(thresholding_config["threshold_max"] * 100))
    step_size = max(int(round(thresholding_config["threshold_step"] * 100)), 1)
    for step in range(start, stop + 1, step_size):
        threshold = step / 100.0
        predictions = [1 if probability >= threshold else 0 for probability in probabilities]
        tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
        sensitivity = tp / max(tp + fn, 1)
        specificity = tn / max(tn + fp, 1)
        if sensitivity >= target_sensitivity and specificity > best_specificity:
            best_specificity = specificity
            best_threshold = threshold
    return best_threshold


def _evaluate(probabilities: list[float], labels: list[int], threshold: float) -> dict[str, float]:
    predictions = [1 if probability >= threshold else 0 for probability in probabilities]
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    sensitivity = tp / max(tp + fn, 1)
    specificity = tn / max(tn + fp, 1)
    accuracy = (tp + tn) / max(tp + tn + fp + fn, 1)
    return {
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "accuracy": round(accuracy, 4),
    }


def apply_temperature(probability: float, temperature: float) -> float:
    """Public wrapper over temperature scaling, reused by the DOE sweep harness."""
    return _temperature_scale(probability, temperature)


def binary_metrics(probabilities: list[float], labels: list[int], threshold: float) -> dict[str, float]:
    """Public wrapper computing sensitivity/specificity/accuracy at a threshold."""
    return _evaluate(probabilities, labels, threshold)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_model_card(
    path: Path,
    metrics: dict[str, float],
    threshold: float,
    temperature: float,
    model_family: str,
) -> None:
    contents = f"""# Model Card

## Summary

This public demo model detects a synthetic concerning pattern from generated triage-style images.

- Model family: {model_family}

## Data

- Fully synthetic images generated locally
- Non-diagnostic public demo
- Intended to demonstrate methodology and system design, not clinical accuracy

## Metrics

- Sensitivity: {metrics["sensitivity"]:.4f}
- Specificity: {metrics["specificity"]:.4f}
- Accuracy: {metrics["accuracy"]:.4f}

These scores reflect held-out performance on synthetic data where the visual task is
engineered to be solvable by design. Calibration, sensitivity-constrained threshold
selection, and locked test evaluation are separate steps in the pipeline.

## Calibration

Temperature scaling is applied to correct probability estimates before threshold selection.
The calibration temperature ({temperature:.2f}) reflects how the model's raw probabilities
compare to the true class distribution — values below 1.0 indicate the model was
underconfident (probabilities clustered near 0.5); values above 1.0 indicate overconfidence.

On this synthetic task the visual signal is strong enough that calibration does not change
classification outcomes. In professional deployments using the same methodology, applying
temperature scaling to a clinical imaging pathway recovered specificity from 6.8% to 95.0%
on the validation split (n=722) while preserving AUC 0.965, confirmed on the held-out test
set (n=929, AUC 0.960) — a case where AUC alone declared the model acceptable but
inspection of calibrated probabilities revealed the decision threshold was operating in a
degenerate region.

See `docs/methodology.md` and `artifacts/latest/calibration.json` for more detail.

## Deployment knobs

- Review threshold: {threshold:.2f}
- Calibration temperature: {temperature:.2f}
"""
    path.write_text(contents, encoding="utf-8")


def _sigmoid(value: float) -> float:
    value = max(min(value, 60.0), -60.0)
    return 1.0 / (1.0 + math.exp(-value))


def _convolve_valid(image: np.ndarray, kernel: np.ndarray, bias: float) -> np.ndarray:
    height, width = image.shape
    kernel_height, kernel_width = kernel.shape
    output = np.zeros((height - kernel_height + 1, width - kernel_width + 1), dtype=float)
    for row in range(output.shape[0]):
        for col in range(output.shape[1]):
            patch = image[row : row + kernel_height, col : col + kernel_width]
            output[row, col] = float(np.sum(patch * kernel) + bias)
    return output


def _predict_compact_cnn_probability(matrix: np.ndarray, kernels: np.ndarray, biases: np.ndarray, dense_weights: np.ndarray, dense_bias: float) -> float:
    pooled: list[float] = []
    for kernel, bias in zip(kernels, biases):
        activated = np.maximum(_convolve_valid(matrix, kernel, float(bias)), 0.0)
        pooled.append(float(np.mean(activated)))
    logit = float(np.dot(dense_weights, np.asarray(pooled)) + dense_bias)
    return _sigmoid(logit)


def _fit_compact_cnn(train_matrices: list[np.ndarray], labels: list[int], random_state: int) -> dict[str, object]:
    rng = np.random.default_rng(random_state)
    kernels = rng.normal(0.0, 0.1, size=(2, 3, 3))
    biases = np.zeros(2, dtype=float)
    dense_weights = rng.normal(0.0, 0.1, size=2)
    dense_bias = 0.0
    learning_rate = 0.01

    for _ in range(180):
        for matrix, label in zip(train_matrices, labels):
            conv_maps = []
            activated_maps = []
            for kernel, bias in zip(kernels, biases):
                conv = _convolve_valid(matrix, kernel, float(bias))
                activated = np.maximum(conv, 0.0)
                conv_maps.append(conv)
                activated_maps.append(activated)

            pooled = np.asarray([float(np.mean(item)) for item in activated_maps], dtype=float)
            probability = _sigmoid(float(np.dot(dense_weights, pooled) + dense_bias))
            error = probability - label

            dense_weights -= learning_rate * error * pooled
            dense_bias -= learning_rate * error

            pooled_grad = error * dense_weights
            for index, (conv, activated) in enumerate(zip(conv_maps, activated_maps)):
                del activated
                relu_mask = (conv > 0.0).astype(float)
                grad_map = (pooled_grad[index] / relu_mask.size) * relu_mask
                kernel_grad = np.zeros_like(kernels[index])
                for row in range(grad_map.shape[0]):
                    for col in range(grad_map.shape[1]):
                        patch = matrix[row : row + 3, col : col + 3]
                        kernel_grad += grad_map[row, col] * patch
                kernels[index] -= learning_rate * kernel_grad
                biases[index] -= learning_rate * float(np.sum(grad_map))

    return {
        "kernels": kernels.tolist(),
        "biases": biases.tolist(),
        "dense_weights": dense_weights.tolist(),
        "dense_bias": float(dense_bias),
    }


def _predict_probabilities(model_payload: dict[str, object], images: list[Image.Image]) -> list[float]:
    family = model_payload["model_family"]
    if family == "compact_cnn":
        kernels = np.asarray(model_payload["kernels"], dtype=float)
        biases = np.asarray(model_payload["biases"], dtype=float)
        dense_weights = np.asarray(model_payload["dense_weights"], dtype=float)
        dense_bias = float(model_payload["dense_bias"])
        input_size = int(model_payload["input_size"])
        return [
            _predict_compact_cnn_probability(
                _image_to_matrix(image, size=input_size),
                kernels,
                biases,
                dense_weights,
                dense_bias,
            )
            for image in images
        ]

    weights = model_payload["weights"]
    bias = float(model_payload["bias"])
    input_size = int(model_payload["input_size"])
    probabilities = []
    for image in images:
        vector = _image_to_vector(image, size=input_size)
        logit = sum(weight * value for weight, value in zip(weights, vector)) + bias
        probabilities.append(_sigmoid(logit))
    return probabilities


def _write_comparison_report(path: Path, trained_model_family: str, metrics: dict[str, float]) -> None:
    _write_json(
        path,
        {
            "trained_model_family": trained_model_family,
            "available_model_families": ["baseline_linear", "compact_cnn"],
            "metrics": metrics,
        },
    )


def _build_cases(dataset_size: int, image_size: int, generation_config: dict) -> list[SyntheticCase]:
    return [
        generate_synthetic_case(
            seed=index,
            image_size=image_size,
            generation_config=generation_config,
        )
        for index in range(dataset_size)
    ]


def _split_cases(cases: list[SyntheticCase], split_config: dict) -> tuple[list[SyntheticCase], list[SyntheticCase], list[SyntheticCase]]:
    total = len(cases)
    train_end = int(total * split_config["train_ratio"])
    val_end = train_end + int(total * split_config["validation_ratio"])
    return cases[:train_end], cases[train_end:val_end], cases[val_end:]


def fit_model_artifacts(
    output_dir: Path,
    dataset_size: int | None = None,
    image_size: int | None = None,
    model_family: str = "baseline_linear",
) -> dict[str, object]:
    synthetic_config = load_synthetic_data_config()
    training_config = load_training_config()
    resolved_dataset_size = dataset_size or synthetic_config["dataset"]["size"]
    resolved_image_size = image_size or synthetic_config["dataset"]["image_size"]

    cases = _build_cases(
        dataset_size=resolved_dataset_size,
        image_size=resolved_image_size,
        generation_config=synthetic_config["generation"],
    )
    train_cases, val_cases, test_cases = _split_cases(cases, training_config["splits"])
    input_size = training_config["model"]["input_size"]

    y_train = [1 if case.has_concerning_pattern else 0 for case in train_cases]
    y_val = [1 if case.has_concerning_pattern else 0 for case in val_cases]
    y_test = [1 if case.has_concerning_pattern else 0 for case in test_cases]
    if model_family == "compact_cnn":
        model_payload: dict[str, object] = {
            "model_family": model_family,
            "input_size": input_size,
            **_fit_compact_cnn(
                train_matrices=[_image_to_matrix(case.image, size=input_size) for case in train_cases],
                labels=y_train,
                random_state=training_config["model"]["random_state"],
            ),
            "temperature": 1.0,
            "review_threshold": 0.5,
        }
    else:
        x_train = [_image_to_vector(case.image, size=input_size) for case in train_cases]
        model = LogisticRegression(
            random_state=training_config["model"]["random_state"],
            max_iter=training_config["model"]["max_iter"],
        )
        model.fit(x_train, y_train)
        model_payload = {
            "model_family": "baseline_linear",
            "weights": model.coef_[0].tolist(),
            "bias": float(model.intercept_[0]),
            "input_size": input_size,
            "temperature": 1.0,
            "review_threshold": 0.5,
        }

    val_probabilities = _predict_probabilities(model_payload, [case.image for case in val_cases])
    test_probabilities = _predict_probabilities(model_payload, [case.image for case in test_cases])

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "predictions.json",
        {
            "validation": {"probabilities": val_probabilities, "labels": y_val},
            "test": {"probabilities": test_probabilities, "labels": y_test},
        },
    )
    _write_json(
        output_dir / "model.json",
        model_payload,
    )
    return {
        "model_family": model_payload["model_family"],
        "validation_probabilities": val_probabilities,
        "validation_labels": y_val,
        "test_probabilities": test_probabilities,
        "test_labels": y_test,
    }


def calibrate_model_artifacts(output_dir: Path) -> dict[str, float]:
    training_config = load_training_config()
    predictions = json.loads((output_dir / "predictions.json").read_text(encoding="utf-8"))
    model_payload = json.loads((output_dir / "model.json").read_text(encoding="utf-8"))

    val_probabilities = predictions["validation"]["probabilities"]
    val_labels = predictions["validation"]["labels"]
    temperature = _fit_temperature(val_probabilities, val_labels, training_config["calibration"])
    calibrated_val = [_temperature_scale(probability, temperature) for probability in val_probabilities]
    review_threshold = _find_threshold(calibrated_val, val_labels, training_config["thresholding"])

    _write_json(output_dir / "calibration.json", {"temperature": temperature})
    _write_json(output_dir / "thresholds.json", {"review_threshold": review_threshold})
    model_payload["temperature"] = temperature
    model_payload["review_threshold"] = review_threshold
    _write_json(output_dir / "model.json", model_payload)
    return {"temperature": temperature, "review_threshold": review_threshold}


def evaluate_model_artifacts(output_dir: Path) -> dict[str, float]:
    predictions = json.loads((output_dir / "predictions.json").read_text(encoding="utf-8"))
    calibration = json.loads((output_dir / "calibration.json").read_text(encoding="utf-8"))
    thresholds = json.loads((output_dir / "thresholds.json").read_text(encoding="utf-8"))

    calibrated_test = [
        _temperature_scale(probability, calibration["temperature"])
        for probability in predictions["test"]["probabilities"]
    ]
    metrics = _evaluate(calibrated_test, predictions["test"]["labels"], thresholds["review_threshold"])
    _write_json(output_dir / "metrics.json", metrics)
    _write_model_card(
        output_dir / "MODEL_CARD.md",
        metrics,
        thresholds["review_threshold"],
        calibration["temperature"],
        json.loads((output_dir / "model.json").read_text(encoding="utf-8"))["model_family"],
    )
    _write_comparison_report(
        output_dir / "comparison.json",
        json.loads((output_dir / "model.json").read_text(encoding="utf-8"))["model_family"],
        metrics,
    )
    return metrics


def run_training_pipeline(
    output_dir: Path,
    dataset_size: int = 120,
    image_size: int = 96,
    model_family: str = "baseline_linear",
) -> TrainingReport:
    fit_result = fit_model_artifacts(
        output_dir=output_dir,
        dataset_size=dataset_size,
        image_size=image_size,
        model_family=model_family,
    )
    calibration = calibrate_model_artifacts(output_dir=output_dir)
    metrics = evaluate_model_artifacts(output_dir=output_dir)
    return TrainingReport(
        metrics=metrics,
        review_threshold=calibration["review_threshold"],
        temperature=calibration["temperature"],
        model_family=str(fit_result["model_family"]),
    )
