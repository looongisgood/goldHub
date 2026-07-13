from datetime import datetime

from fastapi.testclient import TestClient

from app.main import create_app


def fake_github_search(query: str, language: str | None, min_stars: int | None) -> list[dict]:
    assert query == "self-hosted knowledge base"
    assert language == "TypeScript"
    assert min_stars == 100
    return [{
        "id": 1,
        "full_name": "octo/knowledge-base",
        "html_url": "https://github.com/octo/knowledge-base",
        "owner": {"login": "octo", "avatar_url": "https://avatars.githubusercontent.com/u/1"},
        "name": "knowledge-base",
        "description": "A self-hosted knowledge base",
        "stargazers_count": 250,
        "language": "TypeScript",
        "topics": ["knowledge-base", "self-hosted"],
        "license": {"spdx_id": "MIT"},
        "updated_at": "2026-07-01T00:00:00Z",
        "archived": False,
    }]


def client_for(tmp_path) -> TestClient:
    app = create_app(database_url=f"sqlite:///{tmp_path / 'ideahub.db'}", github_search=fake_github_search)
    return TestClient(app)


def test_search_persists_a_ui_ready_dataset(tmp_path) -> None:
    client = client_for(tmp_path)

    response = client.post("/api/search", json={
        "idea": "self-hosted knowledge base",
        "language": "TypeScript",
        "min_stars": 100,
    })

    assert response.status_code == 201
    dataset = response.json()
    assert dataset["idea"] == "self-hosted knowledge base"
    assert dataset["searched_at"].endswith("Z")
    assert datetime.fromisoformat(dataset["searched_at"].replace("Z", "+00:00"))
    assert dataset["github_query"] == "self-hosted knowledge base language:TypeScript stars:>=100"
    assert dataset["projects"] == [{
        "repository_path": "octo/knowledge-base",
        "repository_url": "https://github.com/octo/knowledge-base",
        "image_url": "https://avatars.githubusercontent.com/u/1",
        "name": "knowledge-base",
        "owner": "octo",
        "description": "A self-hosted knowledge base",
        "stars": 250,
        "language": "TypeScript",
        "topics": ["knowledge-base", "self-hosted"],
        "license": "MIT",
        "updated_at": "2026-07-01T00:00:00Z",
        "archived": False,
    }]

    listed = client.get("/api/datasets")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [dataset["id"]]
    assert client.get(f"/api/datasets/{dataset['id']}").json() == dataset


def test_dataset_chat_answers_from_saved_projects(tmp_path) -> None:
    client = client_for(tmp_path)
    dataset_id = client.post("/api/search", json={
        "idea": "self-hosted knowledge base", "language": "TypeScript", "min_stars": 100
    }).json()["id"]

    response = client.post(f"/api/datasets/{dataset_id}/chat", json={"message": "Which project has the most stars?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "octo/knowledge-base has 250 stars."
    assert response.json()["dataset_id"] == dataset_id


def test_dataset_chat_uses_the_question_to_describe_a_matching_project(tmp_path) -> None:
    client = client_for(tmp_path)
    dataset_id = client.post("/api/search", json={
        "idea": "self-hosted knowledge base", "language": "TypeScript", "min_stars": 100
    }).json()["id"]

    response = client.post(f"/api/datasets/{dataset_id}/chat", json={"message": "Tell me about knowledge-base"})

    assert response.status_code == 200
    assert response.json()["answer"] == "octo/knowledge-base: A self-hosted knowledge base"


def test_search_keeps_filters_optional(tmp_path) -> None:
    calls: list[tuple[str, str | None, int | None]] = []

    def search(idea: str, language: str | None, min_stars: int | None) -> list[dict]:
        calls.append((idea, language, min_stars))
        return []

    client = TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'ideahub.db'}", github_search=search))

    response = client.post("/api/search", json={"idea": "local-first notes"})

    assert response.status_code == 201
    assert calls == [("local-first notes", None, None)]
    assert response.json()["github_query"] == "local-first notes"


def test_search_returns_a_clear_upstream_error(tmp_path) -> None:
    def unavailable(_: str, __: str | None, ___: int | None) -> list[dict]:
        raise TimeoutError("GitHub timed out")

    app = create_app(database_url=f"sqlite:///{tmp_path / 'ideahub.db'}", github_search=unavailable)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/api/search", json={"idea": "local-first notes"})

    assert response.status_code == 503
    assert response.json()["detail"] == "GitHub search is temporarily unavailable"


def test_search_drops_projects_without_a_path_or_image(tmp_path) -> None:
    def search(_: str, __: str | None, ___: int | None) -> list[dict]:
        return [{"id": 2}, fake_github_search("self-hosted knowledge base", "TypeScript", 100)[0]]

    client = TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'ideahub.db'}", github_search=search))

    response = client.post("/api/search", json={"idea": "self-hosted knowledge base"})

    assert response.status_code == 201
    assert [project["repository_path"] for project in response.json()["projects"]] == ["octo/knowledge-base"]


def test_health_endpoint_is_available(tmp_path) -> None:
    response = client_for(tmp_path).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
