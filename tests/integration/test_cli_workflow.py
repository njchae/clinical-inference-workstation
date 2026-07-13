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


def test_cli_workflow_should_generate_dataset_train_calibrate_and_evaluate(tmp_path: Path) -> None:
    output_root = tmp_path / "demo-output"
    samples_dir = output_root / "samples"
    artifacts_dir = output_root / "artifacts"
    manifest_path = samples_dir / "examples.json"

    _run_script(
        "generate_dataset.py",
        "--samples-dir",
        str(samples_dir),
        "--manifest-path",
        str(manifest_path),
    )
    _run_script("train_model.py", "--artifact-dir", str(artifacts_dir))
    _run_script("calibrate_model.py", "--artifact-dir", str(artifacts_dir))
    _run_script("evaluate_model.py", "--artifact-dir", str(artifacts_dir))

    assert manifest_path.exists()
    assert (artifacts_dir / "model.json").exists()
    assert (artifacts_dir / "calibration.json").exists()
    assert (artifacts_dir / "metrics.json").exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest) >= 3

