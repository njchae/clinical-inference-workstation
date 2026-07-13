from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.labeling.pipeline import export_reviewed_labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-path", required=True)
    parser.add_argument("--export-path", required=True)
    args = parser.parse_args()

    export_reviewed_labels(
        labels_path=Path(args.labels_path),
        export_path=Path(args.export_path),
    )
    print(f"REVIEWED_LABELS_EXPORTED {args.export_path}")


if __name__ == "__main__":
    main()
