from __future__ import annotations

from typing import Any, Literal

import yaml
from pydantic import BaseModel


def parse_front_matter(text: str) -> dict[str, Any]:
    """Extract and parse the YAML front matter block from a Markdown document."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    return yaml.safe_load(text[4:end]) or {}  # type: ignore[no-any-return]


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


class PoemFrontMatter(BaseModel):
    title: str
    book: str
    book_order: int
    poem_order: int
    book_part: str | None = None
    series: str | None = None
    series_part: str | None = None
    source_pdf: str
    source_pages_scan: list[int] | None = None
    source_pages_printed: list[int] | None = None
    status: Literal["pending", "transcribed", "checked", "final"]
    notes: list[str] = []


class BookFrontMatter(BaseModel):
    title: str | None = None
    book_order: int | None = None
    author: str | None = None
    publisher: str | None = None
    place: str | None = None
    year: int | None = None
    source_pdf: str | None = None
    source_status: str | None = None
    pdf_pages: int | None = None
    rights_status: str | None = None
    transcription_status: str | None = None
    notes: list[str] = []


class VolumeFrontMatter(BaseModel):
    title: str | None = None
    volume_order: int | None = None
    series: str | None = None
