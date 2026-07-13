from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.labeling.pipeline import run_labeling_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--provider", default="local", choices=["local", "openai", "anthropic"])
    parser.add_argument("--checkpoint-path", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--review-queue-path", required=True)
    parser.add_argument("--review-threshold", type=float, default=0.8)
    args = parser.parse_args()

    report = run_labeling_pipeline(
        images_dir=Path(args.images_dir),
        provider_name=args.provider,
        checkpoint_path=Path(args.checkpoint_path),
        output_path=Path(args.output_path),
        review_queue_path=Path(args.review_queue_path),
        review_threshold=args.review_threshold,
    )
    print(f"LABELING_COMPLETE {report.processed_count}")
    print(f"RESUMED_FROM_CHECKPOINT {report.resumed_from_checkpoint}")
    print(f"REVIEW_QUEUE_COUNT {report.review_queue_count}")


if __name__ == "__main__":
    main()
