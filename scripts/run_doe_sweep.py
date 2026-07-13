from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR, load_doe_config
from clinical_inference_workstation.doe.sweep import run_sweep, write_sweep_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a DOE parameter sweep over calibration temperature and threshold.")
    parser.add_argument("--artifact-dir", default=str(ROOT_DIR / "artifacts" / "latest"))
    parser.add_argument(
        "--split",
        choices=["validation", "test"],
        default="validation",
        help="Which split to sweep. Defaults to validation so the test set stays locked.",
    )
    parser.add_argument("--config", default=None, help="Optional path to a DOE config YAML (defaults to configs/doe/threshold_sweep.yaml).")
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir)
    predictions = json.loads((artifact_dir / "predictions.json").read_text(encoding="utf-8"))
    split = predictions[args.split]

    if args.config:
        import yaml

        config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    else:
        config = load_doe_config()

    result = run_sweep(
        probabilities=split["probabilities"],
        labels=split["labels"],
        factors=config["factors"],
        target_sensitivity=config["objective"]["target_sensitivity"],
        design=config.get("design", "full_factorial"),
        fraction=config.get("fraction"),
    )
    paths = write_sweep_artifacts(result, artifact_dir)

    print(f"DOE_SWEEP_COMPLETE {len(result.cells)}")
    print(f"DOE_RESULTS_WRITTEN {paths['results_csv']}")
    if result.best is not None:
        print(
            f"DOE_BEST temperature={result.best.params.get('temperature')} "
            f"threshold={result.best.params.get('threshold')} "
            f"specificity={result.best.specificity:.4f}"
        )
    else:
        print("DOE_BEST none")


if __name__ == "__main__":
    main()
