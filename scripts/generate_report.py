from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR
from clinical_inference_workstation.reporting import write_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Markdown algorithm report from committed artifacts.")
    parser.add_argument("--artifact-dir", default=str(ROOT_DIR / "artifacts" / "latest"))
    parser.add_argument("--output-path", default=str(ROOT_DIR / "output" / "reports" / "algorithm_report.md"))
    args = parser.parse_args()

    written = write_markdown_report(Path(args.artifact_dir), Path(args.output_path))
    print(f"REPORT_WRITTEN {written}")


if __name__ == "__main__":
    main()
