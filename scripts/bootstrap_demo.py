from __future__ import annotations

from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.ml.pipeline import (
    calibrate_model_artifacts,
    evaluate_model_artifacts,
    fit_model_artifacts,
)
from clinical_inference_workstation.ml.synthetic_data import export_sample_cases


def main() -> None:
    artifact_dir = ROOT_DIR / "artifacts" / "latest"
    samples_dir = ROOT_DIR / "web" / "samples"
    export_sample_cases(samples_dir=samples_dir, manifest_path=samples_dir / "examples.json")
    (samples_dir / "favicon.txt").write_text("STW", encoding="utf-8")
    fit_model_artifacts(output_dir=artifact_dir)
    calibrate_model_artifacts(output_dir=artifact_dir)
    evaluate_model_artifacts(output_dir=artifact_dir)
    print(f"BOOTSTRAP_COMPLETE {ROOT_DIR}")


if __name__ == "__main__":
    main()
