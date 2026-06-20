"""Pydantic v2 models for project and workspace resources."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ProjectRef(BaseModel):
    """Lightweight workspace entry — one row in workspace.yaml."""
    id: str
    path: str
    description: str = ""


class CollectionMeta(BaseModel):
    """Contents of collection.yaml."""
    title: str
    author: str
    subtitle: str = ""
    year: int | None = None
    publisher: str = ""
    isbn: str = ""
    content_dir: str = "content"
    output_dir: str = "output"
    lualatex_path: str = "lualatex"
    draft_mode: bool = False


class ProjectDetail(BaseModel):
    """Full project details returned by GET /api/projects/{id}."""
    id: str
    path: str
    description: str = ""
    meta: CollectionMeta
    section_count: int = 0
    poem_count: int = 0
    last_built: str | None = None


class ProjectCreate(BaseModel):
    """Body for POST /api/projects."""
    id: str = Field(..., pattern=r"^[a-z0-9][a-z0-9\-]*$")
    path: str
    description: str = ""
    meta: CollectionMeta


class WorkspaceInfo(BaseModel):
    """Response for GET /api/projects."""
    workspace_path: str
    default_project: str | None = None
    projects: list[ProjectRef]
