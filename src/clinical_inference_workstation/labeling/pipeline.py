from __future__ import annotations

import json
from pathlib import Path

from clinical_inference_workstation.labeling.providers import build_provider
from clinical_inference_workstation.labeling.schemas import LabelResult, LabelingRunReport


def _load_checkpoint(checkpoint_path: Path | None) -> list[LabelResult]:
    if checkpoint_path is None or not checkpoint_path.exists():
        return []
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    return [LabelResult.model_validate(item) for item in payload.get("results", [])]


def _write_checkpoint(checkpoint_path: Path | None, results: list[LabelResult]) -> None:
    if checkpoint_path is None:
        return
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps({"results": [item.model_dump() for item in results]}, indent=2),
        encoding="utf-8",
    )


def _iter_image_paths(images_dir: Path) -> list[Path]:
    return sorted(path for path in images_dir.rglob("*") if path.suffix.lower() in {".png", ".jpg", ".jpeg"})


def _write_review_queue(review_queue_path: Path, results: list[LabelResult]) -> int:
    review_queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue = [item for item in results if item.review_required]
    review_queue_path.write_text(
        "\n".join(json.dumps(item.model_dump()) for item in queue),
        encoding="utf-8",
    )
    return len(queue)


def run_labeling_pipeline(
    *,
    images_dir: Path,
    provider_name: str,
    checkpoint_path: Path | None,
    output_path: Path,
    review_queue_path: Path,
    review_threshold: float,
) -> LabelingRunReport:
    provider = build_provider(provider_name)
    existing = _load_checkpoint(checkpoint_path)
    by_case_id = {item.case_id: item for item in existing}

    for image_path in _iter_image_paths(images_dir):
        if image_path.stem in by_case_id:
            continue
        labeled = provider.label_image(image_path)
        labeled.review_required = labeled.confidence < review_threshold
        by_case_id[labeled.case_id] = labeled
        _write_checkpoint(checkpoint_path, list(by_case_id.values()))

    results = list(sorted(by_case_id.values(), key=lambda item: item.case_id))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([item.model_dump() for item in results], indent=2),
        encoding="utf-8",
    )
    review_queue_count = _write_review_queue(review_queue_path, results)
    _write_checkpoint(checkpoint_path, results)
    return LabelingRunReport(
        processed_count=len(results),
        resumed_from_checkpoint=bool(existing),
        review_queue_count=review_queue_count,
    )


def export_reviewed_labels(*, labels_path: Path, export_path: Path) -> None:
    payload = json.loads(labels_path.read_text(encoding="utf-8"))
    exported: list[dict[str, object]] = []
    for item in payload:
        review_status = item.get("review_status", "pending")
        if review_status != "accepted":
            continue
        label = LabelResult.model_validate(
            {
                "image_path": item.get("image_path", ""),
                "provider": item.get("provider", "review"),
                "confidence": item.get("confidence", 1.0),
                "rationale": item.get("rationale", "reviewed label"),
                "image_quality": item.get("image_quality", "good"),
                "review_required": item.get("review_required", False),
                **item,
            }
        )
        exported.append(
            {
                "case_id": label.case_id,
                "redness_present": label.signals.redness_present,
                "texture_present": label.signals.texture_present,
                "lesion_visible": label.signals.lesion_visible,
            }
        )
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(json.dumps(exported, indent=2), encoding="utf-8")
