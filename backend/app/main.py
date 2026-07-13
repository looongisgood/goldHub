import os
from datetime import UTC
from json import JSONDecodeError
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from .chat import answer_from_dataset
from .database import session_dependency, build_session_factory
from .github import GitHubSearch, build_query, normalize_project, search_public_repositories
from .models import ChatMessage, Dataset, Project


class SearchRequest(BaseModel):
    idea: str = Field(min_length=1)
    language: str | None = None
    min_stars: int | None = Field(default=None, ge=0)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


def serialize_dataset(dataset: Dataset) -> dict:
    searched_at = dataset.created_at
    if searched_at.tzinfo is None:
        searched_at = searched_at.replace(tzinfo=UTC)
    return {
        "id": dataset.id,
        "idea": dataset.idea,
        "searched_at": searched_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "github_query": dataset.github_query,
        "projects": [
            {
                "repository_path": project.repository_path,
                "repository_url": project.repository_url,
                "image_url": project.image_url,
                "name": project.name,
                "owner": project.owner,
                "description": project.description,
                "stars": project.stars,
                "language": project.language,
                "topics": project.topics,
                "license": project.license,
                "updated_at": project.updated_at,
                "archived": project.archived,
            }
            for project in dataset.projects
        ],
    }


def create_app(
    database_url: str | None = None, github_search: GitHubSearch = search_public_repositories
) -> FastAPI:
    database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///backend/data/ideahub.db")
    session_factory = build_session_factory(database_url)
    app = FastAPI(title="IdeaHub API")

    def get_session():
        yield from session_dependency(session_factory)

    def dataset_or_404(session: Session, dataset_id: int) -> Dataset:
        dataset = (
            session.query(Dataset)
            .options(selectinload(Dataset.projects))
            .filter(Dataset.id == dataset_id)
            .one_or_none()
        )
        if dataset is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/search", status_code=status.HTTP_201_CREATED)
    def search(request: SearchRequest, session: Annotated[Session, Depends(get_session)]) -> dict:
        query = build_query(request.idea, request.language, request.min_stars)
        try:
            repositories = github_search(request.idea, request.language, request.min_stars)
        except (OSError, JSONDecodeError) as error:
            raise HTTPException(status_code=503, detail="GitHub search is temporarily unavailable") from error
        dataset = Dataset(idea=request.idea, github_query=query)
        session.add(dataset)
        session.flush()
        for record in map(normalize_project, repositories):
            if not all(record[field] for field in ("repository_path", "repository_url", "image_url", "name", "owner")):
                continue
            session.add(Project(dataset_id=dataset.id, **record))
        session.commit()
        return serialize_dataset(dataset_or_404(session, dataset.id))

    @app.get("/api/datasets")
    def list_datasets(session: Annotated[Session, Depends(get_session)]) -> list[dict]:
        datasets = session.query(Dataset).options(selectinload(Dataset.projects)).order_by(Dataset.id).all()
        return [serialize_dataset(dataset) for dataset in datasets]

    @app.get("/api/datasets/{dataset_id}")
    def get_dataset(dataset_id: int, session: Annotated[Session, Depends(get_session)]) -> dict:
        return serialize_dataset(dataset_or_404(session, dataset_id))

    @app.post("/api/datasets/{dataset_id}/chat")
    def chat(dataset_id: int, request: ChatRequest, session: Annotated[Session, Depends(get_session)]) -> dict:
        dataset = dataset_or_404(session, dataset_id)
        answer = answer_from_dataset(dataset, request.message)
        session.add_all([
            ChatMessage(dataset_id=dataset_id, role="user", content=request.message),
            ChatMessage(dataset_id=dataset_id, role="assistant", content=answer),
        ])
        session.commit()
        return {"dataset_id": dataset_id, "answer": answer}

    return app


app = create_app()
