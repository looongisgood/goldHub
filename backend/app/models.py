from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    idea: Mapped[str] = mapped_column(Text)
    github_query: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    projects: Mapped[list[Project]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", order_by="Project.id"
    )
    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", order_by="ChatMessage.id"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    repository_path: Mapped[str] = mapped_column(String)
    repository_url: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    owner: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stars: Mapped[int] = mapped_column(Integer)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    license: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    dataset: Mapped[Dataset] = relationship(back_populates="projects")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    dataset: Mapped[Dataset] = relationship(back_populates="messages")
