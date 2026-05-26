"""Section router.

section_id in all URL paths == the directory name (e.g. "03_vibrations-dented-spheres").
This is always unique within a project and maps directly to the filesystem.
The id field in _meta.yaml is stored in SectionSummary.meta_id but is NOT used in URLs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from fastapi import APIRouter

from app.core.exceptions import ConflictError, NotFoundError
from app.models.section import SectionCreate, SectionDetail, SectionSummary, SectionUpdate

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

router = APIRouter()


def _section_dir_name(order: int, section_id: str) -> str:
    return f"{order:02d}_{section_id}"


def _section_suffix(dir_name: str) -> str:
    match = re.match(r"^\d+_(.+)$", dir_name)
    return match.group(1) if match else dir_name


def _content_dir(project_id: str) -> Path:
    from app.services import project_service
    detail = project_service.get_project(project_id)
    return Path(detail.path) / detail.meta.content_dir


def _find_section_dir(content_dir: Path, section_id: str) -> Path:
    """Exact match on directory name â€” section_id IS the dir name."""
    d = content_dir / section_id
    if not d.is_dir():
        raise NotFoundError(f"Section '{section_id}' not found")
    return d


@router.get("", response_model=list[SectionSummary])
async def list_sections(project_id: str) -> list[SectionSummary]:
    import yaml
    content_dir = _content_dir(project_id)
    summaries: list[SectionSummary] = []
    for d in sorted(content_dir.iterdir()):
        if not d.is_dir():
            continue
        meta_file = d / "_meta.yaml"
        if not meta_file.exists():
            meta_file = d / "_section.yaml"
        meta: dict = yaml.safe_load(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
        poems = [f for f in d.glob("*.md") if not f.name.startswith("_") and "--" not in f.stem]
        summaries.append(SectionSummary(
            id=d.name,                                  # dir name is the canonical ID
            dir_name=d.name,
            label=meta.get("label", d.name),
            order=meta.get("order", 999),
            poem_count=len(poems),
            section_is_cycle=meta.get("section_is_cycle", False),
        ))
    return sorted(summaries, key=lambda s: s.order)


@router.get("/{section_id}", response_model=SectionDetail)
async def get_section(project_id: str, section_id: str) -> SectionDetail:
    import yaml
    import frontmatter
    content_dir = _content_dir(project_id)
    d = _find_section_dir(content_dir, section_id)
    meta_file = d / "_meta.yaml"
    meta: dict = yaml.safe_load(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    title_page_path = d / "_title.md"
    title_page_title: str | None = None
    poems = [f.stem for f in sorted(d.glob("*.md")) if not f.name.startswith("_") and "--" not in f.stem]
    poem_count = len(poems)
    if title_page_path.exists():
        poems = ["_title", *poems]
        try:
            title_page_title = frontmatter.load(str(title_page_path)).metadata.get("title")
        except Exception:
            title_page_title = None
    return SectionDetail(
        id=d.name,
        dir_name=d.name,
        label=meta.get("label", d.name),
        order=meta.get("order", 999),
        poem_count=poem_count,
        poem_slugs=poems,
        section_is_cycle=meta.get("section_is_cycle", False),
        has_title_page=title_page_path.exists(),
        title_page_slug="_title" if title_page_path.exists() else None,
        title_page_title=title_page_title,
    )


@router.post("", response_model=SectionDetail, status_code=201)
async def create_section(project_id: str, body: SectionCreate) -> SectionDetail:
    import yaml
    content_dir = _content_dir(project_id)
    content_dir.mkdir(parents=True, exist_ok=True)
    dir_name = _section_dir_name(body.order, body.id)
    sec_dir = content_dir / dir_name
    for existing in content_dir.iterdir():
        if existing.is_dir() and _section_suffix(existing.name) == body.id:
            raise ConflictError(f"Section id '{body.id}' already exists as '{existing.name}'")
    if sec_dir.exists():
        raise ConflictError(f"Section '{dir_name}' already exists")
    sec_dir.mkdir(parents=True, exist_ok=False)
    meta = {"id": body.id, "type": "section", "label": body.label, "order": body.order}
    if body.section_is_cycle:
        meta["section_is_cycle"] = True
    (sec_dir / "_meta.yaml").write_text(yaml.dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if body.title_page_title:
        fm_parts = [f'title: "{body.title_page_title}"', "type: section-title", "order: 0"]
        if body.title_page_epigraph:
            fm_parts.append(f'epigraph: "{body.title_page_epigraph}"')
        if body.title_page_epigraph_author:
            fm_parts.append(f'epigraph_author: "{body.title_page_epigraph_author}"')
        (sec_dir / "_title.md").write_text("---\n" + "\n".join(fm_parts) + "\n---\n", encoding="utf-8")
    return await get_section(project_id, dir_name)


@router.patch("/{section_id}", response_model=SectionDetail)
async def update_section(project_id: str, section_id: str, body: SectionUpdate) -> SectionDetail:
    import yaml
    content_dir = _content_dir(project_id)
    d = _find_section_dir(content_dir, section_id)
    meta_file = d / "_meta.yaml"
    meta: dict = yaml.safe_load(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    if body.label is not None:
        meta["label"] = body.label
    if body.order is not None:
        meta["order"] = body.order
    if body.section_is_cycle is not None:
        meta["section_is_cycle"] = body.section_is_cycle
    meta_file.write_text(yaml.dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return await get_section(project_id, section_id)

