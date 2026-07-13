import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_dataset.py"


def valid_dataset() -> dict:
    return {
        "id": "dataset-20260710-001",
        "idea": "self-hosted idea discovery",
        "searched_at": "2026-07-10T12:00:00Z",
        "github_query": "idea discovery language:TypeScript",
        "projects": [{
            "repository_path": "example/ideahub",
            "repository_url": "https://github.com/example/ideahub",
            "image_url": "https://avatars.githubusercontent.com/u/1",
            "name": "ideahub",
            "owner": "example",
            "description": "Example project",
            "stars": 42,
            "language": "TypeScript",
            "topics": ["ideas"],
            "license": "MIT",
            "updated_at": "2026-07-01T00:00:00Z",
            "archived": False,
        }],
    }


def test_accepts_ui_ready_dataset(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(valid_dataset()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(dataset)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr


def test_rejects_missing_project_image(tmp_path: Path) -> None:
    payload = valid_dataset()
    del payload["projects"][0]["image_url"]
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(dataset)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "image_url" in result.stderr


def test_rejects_missing_archived_status(tmp_path: Path) -> None:
    payload = valid_dataset()
    del payload["projects"][0]["archived"]
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(dataset)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "archived" in result.stderr


def test_rejects_secrets_and_invalid_project_types(tmp_path: Path) -> None:
    payload = valid_dataset()
    payload["GITHUB_TOKEN"] = "not-a-real-token"
    project = payload["projects"][0]
    project["stars"] = "250"
    project["topics"] = "knowledge-base"
    project["archived"] = "false"
    project["updated_at"] = "not-a-date"
    project["repository_path"] = "octo/knowledge-base"
    project["owner"] = "octo"
    project["name"] = "knowledge-base"
    project["repository_url"] = "https://github.com/octo/another-repository"
    project["description"] = "Use ghp_123456789012345678901234567890123456 only in a secret manager"
    project["image_url"] = "https://cdn.example.com/avatar.png"
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(dataset)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    for field in ("GITHUB_TOKEN", "stars", "topics", "archived", "updated_at", "repository_path", "repository_url", "description", "image_url"):
        assert field in result.stderr


def test_rejects_malformed_repository_path(tmp_path: Path) -> None:
    payload = valid_dataset()
    payload["projects"][0]["repository_path"] = "octo/"
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(dataset)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "repository_path" in result.stderr


def test_rejects_timezone_less_timestamps(tmp_path: Path) -> None:
    payload = valid_dataset()
    payload["searched_at"] = "2026-07-10T12:00:00"
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(dataset)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "searched_at" in result.stderr
