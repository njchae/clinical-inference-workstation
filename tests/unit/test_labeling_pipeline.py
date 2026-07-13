from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from clinical_inference_workstation.labeling.pipeline import (
    export_reviewed_labels,
    run_labeling_pipeline,
)


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (48, 48), color).save(path)


def test_labeling_pipeline_should_resume_from_checkpoint_and_create_review_queue(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    checkpoint_path = tmp_path / "checkpoint.json"
    output_path = tmp_path / "labels.json"
    review_queue_path = tmp_path / "review_queue.jsonl"
    _write_image(images_dir / "case_a.png", (230, 90, 90))
    _write_image(images_dir / "case_b.png", (205, 205, 205))

    checkpoint_path.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "case_id": "case_a",
                        "image_path": str(images_dir / "case_a.png"),
                        "provider": "local",
                        "confidence": 0.91,
                        "rationale": "already complete",
                        "image_quality": "good",
                        "review_required": False,
                        "signals": {
                            "redness_present": True,
                            "texture_present": False,
                            "lesion_visible": True,
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_labeling_pipeline(
        images_dir=images_dir,
        provider_name="local",
        checkpoint_path=checkpoint_path,
        output_path=output_path,
        review_queue_path=review_queue_path,
        review_threshold=0.8,
    )

    assert result.processed_count == 2
    assert result.resumed_from_checkpoint is True

    labels = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(labels) == 2
    assert {item["case_id"] for item in labels} == {"case_a", "case_b"}

    review_rows = [json.loads(line) for line in review_queue_path.read_text(encoding="utf-8").splitlines()]
    assert len(review_rows) == 1
    assert review_rows[0]["case_id"] == "case_b"


def test_export_reviewed_labels_should_keep_only_accepted_items(tmp_path: Path) -> None:
    labels_path = tmp_path / "reviewed_labels.json"
    export_path = tmp_path / "training_labels.json"
    labels_path.write_text(
        json.dumps(
            [
                {
                    "case_id": "case_a",
                    "review_status": "accepted",
                    "signals": {
                        "redness_present": True,
                        "texture_present": False,
                        "lesion_visible": True,
                    },
                },
                {
                    "case_id": "case_b",
                    "review_status": "rejected",
                    "signals": {
                        "redness_present": False,
                        "texture_present": False,
                        "lesion_visible": False,
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    export_reviewed_labels(labels_path=labels_path, export_path=export_path)

    exported = json.loads(export_path.read_text(encoding="utf-8"))
    assert exported == [
        {
            "case_id": "case_a",
            "redness_present": True,
            "texture_present": False,
            "lesion_visible": True,
        }
    ]
