from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.ml.pipeline import calibrate_model_artifacts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", default=str(ROOT_DIR / "artifacts" / "latest"))
    args = parser.parse_args()

    result = calibrate_model_artifacts(output_dir=Path(args.artifact_dir))
    print(f"CALIBRATION_WRITTEN {args.artifact_dir}")
    print(f"TEMPERATURE {result['temperature']:.4f}")
    print(f"REVIEW_THRESHOLD {result['review_threshold']:.4f}")


if __name__ == "__main__":
    main()
