#!/usr/bin/env python3
"""Validate the stable, UI-ready IdeaHub dataset contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_FIELDS = ("id", "idea", "searched_at", "github_query", "projects")
PROJECT_FIELDS = (
    "repository_path", "repository_url", "image_url", "name", "owner",
    "description", "stars", "language", "topics", "license", "updated_at", "archived",
)
SECRET_MARKERS = ("token", "authorization", "api_key", "secret", "password")
SECRET_VALUE_PATTERN = re.compile(r"\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,})\b")


def is_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def secret_keys(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            if any(marker in str(key).lower() for marker in SECRET_MARKERS):
                found.append(name)
            found.extend(secret_keys(child, name))
        return found
    if isinstance(value, list):
        return [key for index, child in enumerate(value) for key in secret_keys(child, f"{prefix}[{index}]")]
    return []


def secret_values(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        return [match for key, child in value.items() for match in secret_values(child, f"{prefix}.{key}" if prefix else str(key))]
    if isinstance(value, list):
        return [match for index, child in enumerate(value) for match in secret_values(child, f"{prefix}[{index}]")]
    if isinstance(value, str) and SECRET_VALUE_PATTERN.search(value):
        return [prefix]
    return []


def errors_for(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["dataset must be a JSON object"]

    errors = [f"missing root field: {field}" for field in ROOT_FIELDS if not payload.get(field)]
    errors.extend(f"dataset contains forbidden secret field: {key}" for key in secret_keys(payload))
    errors.extend(f"dataset contains credential-like value in: {key}" for key in secret_values(payload))
    for field in ("id", "idea", "github_query"):
        if field in payload and not isinstance(payload[field], str):
            errors.append(f"{field} must be a string")
    if "searched_at" in payload and not is_timestamp(payload["searched_at"]):
        errors.append("searched_at must be an RFC 3339 timestamp")

    projects = payload.get("projects")
    if not isinstance(projects, list) or not projects:
        return errors + ["projects must be a non-empty array"]

    string_fields = ("repository_path", "repository_url", "image_url", "name", "owner", "description", "language", "license")
    for index, project in enumerate(projects):
        prefix = f"projects[{index}]"
        if not isinstance(project, dict):
            errors.append(f"{prefix} must be an object")
            continue
        errors.extend(f"{prefix} missing field: {field}" for field in PROJECT_FIELDS if field not in project or project[field] == "")
        for field in string_fields:
            if field in project and not isinstance(project[field], str):
                errors.append(f"{prefix} {field} must be a string")
        if "stars" in project and (not isinstance(project["stars"], int) or isinstance(project["stars"], bool) or project["stars"] < 0):
            errors.append(f"{prefix} stars must be a non-negative integer")
        if "topics" in project and (not isinstance(project["topics"], list) or not all(isinstance(topic, str) and topic for topic in project["topics"])):
            errors.append(f"{prefix} topics must be an array of non-empty strings")
        if "archived" in project and not isinstance(project["archived"], bool):
            errors.append(f"{prefix} archived must be a boolean")
        if "updated_at" in project and not is_timestamp(project["updated_at"]):
            errors.append(f"{prefix} updated_at must be an RFC 3339 timestamp")

        path = project.get("repository_path")
        if isinstance(path, str):
            parts = path.split("/")
            if len(parts) != 2 or not all(parts):
                errors.append(f"{prefix} repository_path must be owner/repository")
            elif project.get("owner") != parts[0] or project.get("name") != parts[1]:
                errors.append(f"{prefix} repository_path must match owner and name")
            elif project.get("repository_url") != f"https://github.com/{path}":
                errors.append(f"{prefix} repository_url must exactly match repository_path")
        if "image_url" in project and (not isinstance(project["image_url"], str) or not project["image_url"].startswith("https://avatars.githubusercontent.com/")):
            errors.append(f"{prefix} image_url must be a GitHub owner-avatar HTTPS URL")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True, help="dataset JSON file")
    args = parser.parse_args()
    try:
        payload = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read dataset: {error}", file=sys.stderr)
        return 1
    errors = errors_for(payload)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"valid IdeaHub dataset: {args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
