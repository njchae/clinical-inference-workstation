from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_adjudication_cli_should_generate_results_trace_and_escalations(tmp_path: Path) -> None:
    labels_path = tmp_path / "labels.json"
    labels_path.write_text(
        json.dumps(
            [
                {
                    "case_id": "case_cli",
                    "image_path": "web/samples/case_cli.png",
                    "provider": "local",
                    "confidence": 0.58,
                    "rationale": "Low-confidence weak label.",
                    "image_quality": "good",
                    "review_required": True,
                    "review_status": "pending",
                    "signals": {
                        "redness_present": True,
                        "texture_present": False,
                        "lesion_visible": False,
                    },
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "adjudication_results.json"
    trace_path = tmp_path / "adjudication_trace.json"
    escalation_path = tmp_path / "escalations.jsonl"

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_adjudication_workflow.py"),
            "--labels-path",
            str(labels_path),
            "--output-path",
            str(output_path),
            "--trace-path",
            str(trace_path),
            "--escalation-path",
            str(escalation_path),
            "--provider",
            "local",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "ADJUDICATION_COMPLETE 1" in completed.stdout
    assert "ESCALATION_COUNT 1" in completed.stdout
    assert output_path.exists()
    assert trace_path.exists()
    assert escalation_path.exists()
