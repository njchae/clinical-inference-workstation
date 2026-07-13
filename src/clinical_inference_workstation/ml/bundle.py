from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from clinical_inference_workstation.ml.pipeline import _image_to_matrix, _image_to_vector, _predict_compact_cnn_probability


@dataclass(frozen=True)
class ModelBundle:
    model_family: str
    weights: list[float]
    bias: float
    temperature: float
    input_size: int
    kernels: list[list[list[float]]] | None = None
    biases: list[float] | None = None
    dense_weights: list[float] | None = None
    dense_bias: float | None = None

    def predict_probability(self, image: Image.Image) -> float:
        if self.model_family == "compact_cnn":
            raw_probability = _predict_compact_cnn_probability(
                _image_to_matrix(image, size=self.input_size),
                np.asarray(self.kernels, dtype=float),
                np.asarray(self.biases, dtype=float),
                np.asarray(self.dense_weights, dtype=float),
                float(self.dense_bias),
            )
        else:
            vector = _image_to_vector(image, size=self.input_size)
            logit = sum(weight * value for weight, value in zip(self.weights, vector)) + self.bias
            raw_probability = 1.0 / (1.0 + math.exp(-logit))
        raw_probability = min(max(raw_probability, 1e-6), 1 - 1e-6)
        scaled_logit = math.log(raw_probability / (1 - raw_probability)) / self.temperature
        calibrated = 1.0 / (1.0 + math.exp(-scaled_logit))
        return round(calibrated, 4)


def load_model_bundle(output_dir: Path) -> ModelBundle:
    payload = json.loads((output_dir / "model.json").read_text(encoding="utf-8"))
    return ModelBundle(
        model_family=payload.get("model_family", "baseline_linear"),
        weights=payload.get("weights", []),
        bias=payload.get("bias", 0.0),
        temperature=payload["temperature"],
        input_size=payload["input_size"],
        kernels=payload.get("kernels"),
        biases=payload.get("biases"),
        dense_weights=payload.get("dense_weights"),
        dense_bias=payload.get("dense_bias"),
    )
