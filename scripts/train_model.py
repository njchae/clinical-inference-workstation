from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.ml.pipeline import fit_model_artifacts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", default=str(ROOT_DIR / "artifacts" / "latest"))
    parser.add_argument("--model-family", default="baseline_linear", choices=["baseline_linear", "compact_cnn"])
    args = parser.parse_args()

    output_dir = Path(args.artifact_dir)
    fit_model_artifacts(output_dir=output_dir, model_family=args.model_family)
    print(f"MODEL_ARTIFACTS_WRITTEN {output_dir}")
    print(f"MODEL_FAMILY {args.model_family}")
    print("MODEL_STAGE complete")


if __name__ == "__main__":
    main()
