"""Pydantic v2 models for collection sections."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SectionMeta(BaseModel):
    """Mirrors _meta.yaml content."""
    id: str
    type: str = "section"
    label: str
    order: int
    section_is_cycle: bool = False


class SectionSummary(BaseModel):
    """One row in section list."""
    id: str
    dir_name: str
    label: str
    order: int
    poem_count: int = 0
    section_is_cycle: bool = False


class SectionDetail(SectionSummary):
    """Full section detail with poem list."""
    poem_slugs: list[str] = Field(default_factory=list)
    has_title_page: bool = False
    title_page_slug: str | None = None
    title_page_title: str | None = None
    render_config: dict[str, object] | None = None


class SectionCreate(BaseModel):
    """Body for POST .../sections."""
    id: str = Field(..., pattern=r"^[a-z0-9][a-z0-9_-]*$")
    label: str
    order: int
    section_is_cycle: bool = False
    title_page_title: str = ""
    title_page_epigraph: str = ""
    title_page_epigraph_author: str = ""


class SectionUpdate(BaseModel):
    """Body for PATCH .../sections/{id}."""
    label: str | None = None
    order: int | None = None
    section_is_cycle: bool | None = None
