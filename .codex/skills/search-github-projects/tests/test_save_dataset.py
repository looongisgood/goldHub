import json
import subprocess
import sys
from pathlib import Path

from test_validate_dataset import valid_dataset


ROOT = Path(__file__).resolve().parents[1]
SAVER = ROOT / "scripts" / "save_dataset.py"


def test_saves_once_and_never_overwrites_existing_dataset(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps(valid_dataset()), encoding="utf-8")
    output = tmp_path / "datasets" / "dataset-20260710-001.json"
    command = [sys.executable, str(SAVER), "--file", str(source), "--out", str(output)]

    first = subprocess.run(command, text=True, capture_output=True)
    second = subprocess.run(command, text=True, capture_output=True)

    assert first.returncode == 0, first.stderr
    assert output.exists()
    assert second.returncode == 1
    assert "already exists" in second.stderr
