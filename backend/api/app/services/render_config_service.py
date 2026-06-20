"""Per-element render configuration cascade service.

Config resolves in order: Global â†’ Section â†’ Poem â†’ Custom (ad-hoc).
Reads collection.yaml render_config block, section _render_config.yaml,
and poem frontmatter render_config block.
"""

from __future__ import annotations

import sys
from pathlib import Path

import frontmatter as fm
import yaml

from app.models.render_config import (
    MergedRenderConfig,
    RenderConfigLayer,
    RenderConfigUpdate,
    RenderConfigValues,
)
from app.services import poem_service, project_service, version_service

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def _project_root(project_id: str) -> Path:
    return Path(project_service.get_project(project_id).path)


def _content_dir(project_id: str) -> Path:
    cfg = project_service.get_project(project_id)
    return Path(cfg.path) / cfg.meta.content_dir


def _section_dir(project_id: str, section_id: str) -> Path:
    section_dir = _content_dir(project_id) / section_id
    return section_dir


def _coerce_values(data: dict[str, object] | None) -> RenderConfigValues:
    payload = data or {}
    return RenderConfigValues(**{k: v for k, v in payload.items() if k in RenderConfigValues.model_fields})


def get_global(project_id: str) -> RenderConfigLayer:
    root = _project_root(project_id)
    collection_yaml = root / "collection.yaml"
    data = yaml.safe_load(collection_yaml.read_text(encoding="utf-8")) or {} if collection_yaml.exists() else {}
    rc = data.get("render_config", {}) or {}
    return RenderConfigLayer(
        level="global",
        values=_coerce_values(rc),
        source_file=str(collection_yaml),
    )


def get_section(project_id: str, section_id: str) -> RenderConfigLayer:
    sec_dir = _section_dir(project_id, section_id)
    if not sec_dir.is_dir():
        return RenderConfigLayer(level="section", scope_id=section_id, values=RenderConfigValues())
    rc_file = sec_dir / "_render_config.yaml"
    rc = yaml.safe_load(rc_file.read_text(encoding="utf-8")) if rc_file.exists() else {}
    return RenderConfigLayer(
        level="section",
        scope_id=section_id,
        values=_coerce_values(rc),
        source_file=str(rc_file),
    )


def get_poem(project_id: str, section_id: str, poem_slug: str) -> RenderConfigLayer:
    sec_dir = poem_service._section_dir(project_id, section_id)
    poem_path = version_service.canonical_path(sec_dir, poem_slug)
    post = fm.load(str(poem_path))
    rc = post.metadata.get("render_config", {}) or {}
    return RenderConfigLayer(
        level="poem",
        scope_id=poem_slug,
        values=_coerce_values(rc),
        source_file=str(poem_path),
    )


def get_merged(project_id: str, section_id: str | None = None, poem_slug: str | None = None) -> MergedRenderConfig:
    layers: list[RenderConfigLayer] = [get_global(project_id)]
    if section_id:
        layers.append(get_section(project_id, section_id))
    if section_id and poem_slug:
        layers.append(get_poem(project_id, section_id, poem_slug))
    resolved = RenderConfigValues()
    for layer in layers:
        for field in RenderConfigValues.model_fields:
            v = getattr(layer.values, field)
            if v is not None:
                setattr(resolved, field, v)
    return MergedRenderConfig(layers=layers, resolved=resolved)


def update_config(project_id: str, body: RenderConfigUpdate) -> MergedRenderConfig:
    if body.level == "global":
        root = _project_root(project_id)
        collection_yaml = root / "collection.yaml"
        data = yaml.safe_load(collection_yaml.read_text(encoding="utf-8")) if collection_yaml.exists() else {}
        data = data or {}
        data["render_config"] = {**data.get("render_config", {}), **body.values.model_dump(exclude_none=True)}
        collection_yaml.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    elif body.level == "section" and body.scope_id:
        sec_dir = _section_dir(project_id, body.scope_id)
        if sec_dir.is_dir():
            rc_file = sec_dir / "_render_config.yaml"
            existing = yaml.safe_load(rc_file.read_text(encoding="utf-8")) if rc_file.exists() else {}
            merged = {**(existing or {}), **body.values.model_dump(exclude_none=True)}
            rc_file.write_text(yaml.dump(merged, allow_unicode=True, sort_keys=False), encoding="utf-8")
    elif body.level == "poem" and body.scope_id:
        if ":" not in body.scope_id:
            return get_merged(project_id)
        section_id, poem_slug = body.scope_id.split(":", 1)
        sec_dir = poem_service._section_dir(project_id, section_id)
        poem_path = version_service.canonical_path(sec_dir, poem_slug)
        post = fm.load(str(poem_path))
        current = dict(post.metadata.get("render_config") or {})
        post.metadata["render_config"] = {**current, **body.values.model_dump(exclude_none=True)}
        poem_path.write_text(fm.dumps(post), encoding="utf-8")
        return get_merged(project_id, section_id, poem_slug)
    return get_merged(project_id, body.scope_id if body.level == "section" else None)

