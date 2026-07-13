from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.labeling.adjudication import run_adjudication_workflow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-path", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--trace-path", required=True)
    parser.add_argument("--escalation-path", required=True)
    parser.add_argument("--provider", default="local", choices=["local", "openai", "anthropic"])
    args = parser.parse_args()

    report = run_adjudication_workflow(
        labels_path=Path(args.labels_path),
        output_path=Path(args.output_path),
        trace_path=Path(args.trace_path),
        escalation_path=Path(args.escalation_path),
        provider_name=args.provider,
    )
    print(f"ADJUDICATION_COMPLETE {report.processed_count}")
    print(f"ESCALATION_COUNT {report.escalation_count}")
    print(f"ADJUDICATION_PROVIDER {report.provider_name}")


if __name__ == "__main__":
    main()
