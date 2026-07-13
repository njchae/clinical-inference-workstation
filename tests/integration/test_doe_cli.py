from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_script(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script_name), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def test_should_write_doe_artifacts_and_report_completion(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "predictions.json").write_text(
        json.dumps(
            {
                "validation": {"probabilities": [0.9, 0.6, 0.4, 0.1], "labels": [1, 1, 0, 0]},
                "test": {"probabilities": [0.8, 0.55, 0.45, 0.2], "labels": [1, 1, 0, 0]},
            }
        )
    )

    completed = _run_script(
        "run_doe_sweep.py",
        "--artifact-dir",
        str(artifact_dir),
        "--split",
        "validation",
    )

    assert "DOE_SWEEP_COMPLETE" in completed.stdout
    assert (artifact_dir / "doe_results.csv").exists()
    summary = json.loads((artifact_dir / "doe_summary.json").read_text(encoding="utf-8"))
    assert summary["n_cells"] >= 1
