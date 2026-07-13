from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.ml.synthetic_data import export_sample_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-dir", default=str(ROOT_DIR / "web" / "samples"))
    parser.add_argument("--manifest-path", default=str(ROOT_DIR / "web" / "samples" / "examples.json"))
    args = parser.parse_args()

    samples_dir = Path(args.samples_dir)
    export_sample_cases(samples_dir=samples_dir, manifest_path=Path(args.manifest_path))
    (samples_dir / "favicon.txt").write_text("STW", encoding="utf-8")
    print(f"DATASET_GENERATED {args.manifest_path}")


if __name__ == "__main__":
    main()
