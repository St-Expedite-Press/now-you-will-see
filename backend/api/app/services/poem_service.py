"""CRUD operations for individual poem files.

section_id in all calls == the directory name (e.g. "03_vibrations-dented-spheres").
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

import frontmatter as fm
import yaml

from app.core.exceptions import ConflictError, NotFoundError
from app.models.poem import PoemCreate, PoemDetail, PoemFrontmatter, PoemRaw, PoemSummary, PoemUpdate
from app.services import project_service, version_service

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def _normalize_poem_type(raw_type: object) -> str:
    value = str(raw_type or "poem").lower().strip()
    if value == "poem cycle":
        return "poem-cycle"
    if value == "prose-poem":
        return "prose"
    return value


def _section_dir(project_id: str, section_id: str) -> Path:
    """Return the section directory; section_id is the exact directory name."""
    cfg = project_service.get_project(project_id)
    sec_dir = Path(cfg.path) / cfg.meta.content_dir / section_id
    if not sec_dir.is_dir():
        raise NotFoundError(f"Section '{section_id}' not found in '{project_id}'")
    return sec_dir


def _title_page_path(sec_dir: Path) -> Path:
    return sec_dir / "_title.md"


def _resolve_poem_path(sec_dir: Path, poem_slug: str) -> Path:
    if poem_slug == "_title":
        path = _title_page_path(sec_dir)
        if not path.exists():
            raise NotFoundError("Section title page not found")
        return path
    return version_service.canonical_path(sec_dir, poem_slug)


def _build_poem_detail(path: Path, poem_slug: str, section_id: str, canonical_filename: str | None = None) -> PoemDetail:
    raw_content = path.read_text(encoding="utf-8")
    post = fm.loads(raw_content)
    raw_frontmatter = dict(post.metadata)
    structured_frontmatter = {
        **raw_frontmatter,
        "title": raw_frontmatter.get("title", poem_slug if poem_slug != "_title" else path.stem),
        "type": _normalize_poem_type(raw_frontmatter.get("type", "poem")),
        "order": raw_frontmatter.get("order"),
        "epigraph": raw_frontmatter.get("epigraph") or "",
        "epigraph_author": raw_frontmatter.get("epigraph_author") or "",
        "dedication": raw_frontmatter.get("dedication") or "",
        "subtitle": raw_frontmatter.get("subtitle") or "",
        "cycle": raw_frontmatter.get("cycle") or "",
        "cycle_part": raw_frontmatter.get("cycle_part"),
    }
    fm_data = PoemFrontmatter(**structured_frontmatter)
    lines = [line for line in post.content.splitlines() if line.strip()]
    canonical_name = canonical_filename or path.name
    return PoemDetail(
        slug=poem_slug,
        filename=path.name,
        frontmatter=fm_data,
        raw_frontmatter=raw_frontmatter,
        raw_content=raw_content,
        body=post.content,
        line_count=len(lines),
        section_id=section_id,
        canonical_filename=canonical_name,
        is_canonical=path.name == canonical_name,
    )


def _parse_frontmatter_text(content: str) -> tuple[dict[str, object], str] | None:
    try:
        post = fm.loads(content)
    except Exception:
        return None

    metadata = post.metadata if isinstance(post.metadata, Mapping) else {}
    return dict(metadata), post.content


def _serialize_frontmatter(metadata: dict[str, object], body: str) -> str:
    yaml_text = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).rstrip()
    if not yaml_text:
        return body
    if body:
        return f"---\n{yaml_text}\n---\n\n{body}"
    return f"---\n{yaml_text}\n---\n"


def _merge_unknown_frontmatter(existing_text: str, incoming_text: str) -> str:
    existing = _parse_frontmatter_text(existing_text)
    incoming = _parse_frontmatter_text(incoming_text)
    if existing is None or incoming is None:
        return incoming_text

    existing_meta, _ = existing
    incoming_meta, incoming_body = incoming
    merged_meta = dict(incoming_meta)
    for key, value in existing_meta.items():
        if key not in merged_meta:
            merged_meta[key] = value
    return _serialize_frontmatter(merged_meta, incoming_body)


def list_poems(project_id: str, section_id: str) -> list[PoemSummary]:
    sec_dir = _section_dir(project_id, section_id)
    summaries: list[PoemSummary] = []
    title_path = _title_page_path(sec_dir)
    if title_path.exists():
        try:
            post = fm.load(str(title_path))
            lines = [line for line in post.content.splitlines() if line.strip()]
            summaries.append(PoemSummary(
                slug="_title",
                title=post.metadata.get("title", "Section Title"),
                type=_normalize_poem_type(post.metadata.get("type", "section-title")),
                order=post.metadata.get("order"),
                line_count=len(lines),
                version_count=1,
                is_canonical=True,
            ))
        except Exception:
            pass
    for path in sorted(sec_dir.glob("*.md")):
        if path.name.startswith("_") or path.name.startswith(".") or "--" in path.stem:
            continue
        try:
            slug = path.stem
            canonical = version_service.canonical_path(sec_dir, slug)
            post = fm.load(str(canonical))
            slug = path.stem
            lines = [l for l in post.content.splitlines() if l.strip()]
            version_list = version_service.list_versions(sec_dir, slug)
            summaries.append(PoemSummary(
                slug=slug,
                title=post.metadata.get("title", slug),
                type=_normalize_poem_type(post.metadata.get("type", "poem")),
                order=post.metadata.get("order"),
                line_count=len(lines),
                version_count=len(version_list.versions),
                is_canonical=version_list.canonical == canonical.name,
            ))
        except Exception:
            continue
    return summaries


def get_poem(project_id: str, section_id: str, poem_slug: str) -> PoemDetail:
    sec_dir = _section_dir(project_id, section_id)
    path = _resolve_poem_path(sec_dir, poem_slug)
    canonical_name = path.name if poem_slug == "_title" else version_service.canonical_filename(sec_dir, poem_slug)
    return _build_poem_detail(path, poem_slug, section_id, canonical_filename=canonical_name)


def get_poem_raw(project_id: str, section_id: str, poem_slug: str) -> PoemRaw:
    sec_dir = _section_dir(project_id, section_id)
    path = _resolve_poem_path(sec_dir, poem_slug)
    return PoemRaw(slug=poem_slug, raw_content=path.read_text(encoding="utf-8"))


def create_poem(project_id: str, section_id: str, body: PoemCreate) -> PoemDetail:
    from backend.core.utils import poem_scaffold, slugify
    sec_dir = _section_dir(project_id, section_id)
    slug = slugify(body.title)
    dest = sec_dir / f"{slug}.md"
    if dest.exists():
        raise ConflictError(f"Poem file '{slug}.md' already exists")
    content = poem_scaffold(title=body.title, poem_type=body.type)
    if body.order is not None:
        content = content.replace("order:\n", f"order: {body.order}\n")
    dest.write_text(content, encoding="utf-8")
    return get_poem(project_id, section_id, slug)


def update_poem(project_id: str, section_id: str, poem_slug: str, body: PoemUpdate) -> PoemDetail:
    sec_dir = _section_dir(project_id, section_id)
    if poem_slug == "_title":
        path = _resolve_poem_path(sec_dir, poem_slug)
        path.write_text(_merge_unknown_frontmatter(path.read_text(encoding="utf-8"), body.content), encoding="utf-8")
        return _build_poem_detail(path, poem_slug, section_id, canonical_filename=path.name)

    path = version_service.resolve_save_path(sec_dir, poem_slug, body.content)
    merged_content = _merge_unknown_frontmatter(path.read_text(encoding="utf-8"), body.content)
    path.write_text(merged_content, encoding="utf-8")
    canonical_name = version_service.canonical_filename(sec_dir, poem_slug)
    return _build_poem_detail(path, poem_slug, section_id, canonical_filename=canonical_name)


def delete_poem(project_id: str, section_id: str, poem_slug: str) -> None:
    sec_dir = _section_dir(project_id, section_id)
    path = sec_dir / f"{poem_slug}.md"
    if not path.exists():
        raise NotFoundError(f"Poem '{poem_slug}' not found")
    sidecar = sec_dir / f".{poem_slug}.versions.yaml"
    if sidecar.exists():
        versions = version_service.list_versions(sec_dir, poem_slug)
        for entry in versions.versions:
            variant_path = sec_dir / entry.file
            if variant_path.exists():
                variant_path.unlink()
        sidecar.unlink()
    if path.exists():
        path.unlink()

