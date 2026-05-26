"""Pydantic v2 models for poems."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PoemType = Literal[
    "poem",
    "prose",
    "poem-cycle",
    "poem-screenplay",
    "section-title",
    "halftitle",
    "titlepage",
    "copyright",
    "dedication",
    "epigraph",
    "toc",
    "notes",
    "index",
    "acknowledgments",
    "about-author",
    "colophon",
]


class PoemFrontmatter(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str
    type: PoemType = "poem"
    order: int | None = None
    epigraph: str = ""
    epigraph_author: str = ""
    dedication: str = ""
    subtitle: str = ""
    cycle: str = ""
    cycle_part: int | None = None


class PoemSummary(BaseModel):
    """Card chip data — everything needed to render a card chip in the browser."""
    slug: str
    title: str
    type: PoemType
    order: int | None
    line_count: int = 0
    version_count: int = 1
    has_warning: bool = False
    warning_message: str = ""
    is_canonical: bool = True


class PoemDetail(BaseModel):
    """Full poem returned by GET .../poems/{slug}."""
    slug: str
    filename: str
    frontmatter: PoemFrontmatter
    raw_frontmatter: dict[str, object] = Field(default_factory=dict)
    raw_content: str = ""
    body: str
    line_count: int = 0
    section_id: str = ""
    canonical_filename: str = ""
    is_canonical: bool = True


class PoemCreate(BaseModel):
    title: str
    type: PoemType = "poem"
    order: int | None = None


class PoemUpdate(BaseModel):
    """Raw Markdown content update (frontmatter + body as single string)."""
    content: str


class PoemRaw(BaseModel):
    """Full raw Markdown string returned alongside structured fields."""
    slug: str
    raw_content: str
