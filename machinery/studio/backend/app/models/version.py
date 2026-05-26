"""Pydantic v2 models for the poem versioning / card-stack system."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VersionEntry(BaseModel):
    file: str
    label: str = ""
    created: str = ""
    lines: int = 0
    is_canonical: bool = False


class VersionSidecar(BaseModel):
    """Contents of .poem-slug.versions.yaml."""
    canonical: str
    versions: list[VersionEntry] = Field(default_factory=list)


class VersionList(BaseModel):
    slug: str
    canonical: str
    versions: list[VersionEntry]
    previous_canonical: str | None = None
    changed: bool = False


class VersionCreate(BaseModel):
    """Body for POST .../versions — create a new variant from existing content."""
    label: str
    source_file: str | None = None  # copy from this file; if None, copies canonical


class VersionSetCanonical(BaseModel):
    """Body for POST .../versions/canonical."""
    file: str


class VersionUpdate(BaseModel):
    label: str | None = None
