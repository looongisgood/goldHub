from __future__ import annotations

import json
import os
from collections.abc import Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GitHubSearch = Callable[[str, str | None, int | None], list[dict]]


def build_query(idea: str, language: str | None, min_stars: int | None) -> str:
    parts = [idea]
    if language:
        parts.append(f"language:{language}")
    if min_stars is not None:
        parts.append(f"stars:>={min_stars}")
    return " ".join(parts)


def search_public_repositories(
    idea: str, language: str | None, min_stars: int | None
) -> list[dict]:
    query = build_query(idea, language, min_stars)
    request = Request(
        f"https://api.github.com/search/repositories?{urlencode({'q': query, 'per_page': 20, 'sort': 'stars', 'order': 'desc'})}",
        headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.getenv("GITHUB_TOKEN") else {}),
        },
    )
    with urlopen(request, timeout=15) as response:  # nosec B310 - GitHub API endpoint is fixed above
        items = json.load(response).get("items", [])
    if not isinstance(items, list):
        return []
    seen_ids: set[int] = set()
    deduplicated: list[dict] = []
    for item in items:
        repository_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(repository_id, int) or repository_id in seen_ids:
            continue
        seen_ids.add(repository_id)
        deduplicated.append(item)
    return deduplicated


def normalize_project(repository: dict) -> dict:
    owner = repository.get("owner") or {}
    license_data = repository.get("license") or {}
    return {
        "repository_path": repository.get("full_name") or "",
        "repository_url": repository.get("html_url") or "",
        "image_url": owner.get("avatar_url") or "",
        "name": repository.get("name") or "",
        "owner": owner.get("login") or "",
        "description": repository.get("description") or "No description provided.",
        "stars": repository.get("stargazers_count") or 0,
        "language": repository.get("language") or "Unknown",
        "topics": repository.get("topics") or [],
        "license": license_data.get("spdx_id") or "Unknown",
        "updated_at": repository.get("updated_at") or "",
        "archived": bool(repository.get("archived")),
    }
