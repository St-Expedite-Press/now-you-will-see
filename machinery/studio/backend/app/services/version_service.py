"""Poem versioning / card-stack system.

Manages .poem-slug.versions.yaml sidecar files and resolves canonical paths.
Called by the compiler (via build_service) before each build.
"""

from __future__ import annotations

import shutil
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import yaml

from app.core.exceptions import ConflictError, NotFoundError
from app.models.version import VersionCreate, VersionEntry, VersionList, VersionSetCanonical, VersionSidecar


def _sidecar_path(section_dir: Path, slug: str) -> Path:
    return section_dir / f".{slug}.versions.yaml"


def _load_sidecar(section_dir: Path, slug: str) -> VersionSidecar | None:
    path = _sidecar_path(section_dir, slug)
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = [VersionEntry(**v) for v in data.get("versions", [])]
    return VersionSidecar(canonical=data.get("canonical", f"{slug}.md"), versions=entries)


def _save_sidecar(section_dir: Path, slug: str, sidecar: VersionSidecar) -> None:
    path = _sidecar_path(section_dir, slug)
    data = {"canonical": sidecar.canonical, "versions": [v.model_dump() for v in sidecar.versions]}
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _version_files(section_dir: Path, slug: str) -> list[str]:
    sidecar = _load_sidecar(section_dir, slug)
    files: list[str] = [f"{slug}.md"]
    if sidecar is not None:
        for entry in sidecar.versions:
            if entry.file not in files:
                files.append(entry.file)
        if sidecar.canonical not in files:
            files.append(sidecar.canonical)
    return files


def canonical_filename(section_dir: Path, slug: str) -> str:
    """Return the canonical filename for a slug, defaulting to slug.md."""
    sidecar = _load_sidecar(section_dir, slug)
    candidate = sidecar.canonical if sidecar is not None else f"{slug}.md"
    return candidate


def canonical_path(section_dir: Path, slug: str) -> Path:
    """Return the canonical path for a slug, validating that it exists."""
    path = section_dir / canonical_filename(section_dir, slug)
    if not path.exists():
        raise NotFoundError(f"Poem '{slug}' not found")
    return path


def _ensure_canonical_entry(sidecar: VersionSidecar, slug: str, section_dir: Path) -> VersionSidecar:
    """Ensure the canonical file is represented in the sidecar."""
    files = {entry.file for entry in sidecar.versions}
    if sidecar.canonical not in files:
        canonical_path_value = section_dir / sidecar.canonical
        if canonical_path_value.exists():
            lines = len([l for l in canonical_path_value.read_text(encoding="utf-8").splitlines() if l.strip()])
            sidecar.versions.append(
                VersionEntry(
                    file=sidecar.canonical,
                    label="Current" if sidecar.canonical == f"{slug}.md" else sidecar.canonical,
                    created=str(date.today()),
                    lines=lines,
                )
            )
    return sidecar


def list_versions(section_dir: Path, slug: str) -> VersionList:
    sidecar = _load_sidecar(section_dir, slug)
    if sidecar is None:
        poem_path = canonical_path(section_dir, slug)
        lines = len([l for l in poem_path.read_text(encoding="utf-8").splitlines() if l.strip()])
        return VersionList(
            slug=slug,
            canonical=poem_path.name,
            versions=[VersionEntry(file=poem_path.name, label="Current", lines=lines, is_canonical=True)],
        )
    sidecar = _ensure_canonical_entry(sidecar, slug, section_dir)
    entries = [VersionEntry(**{**v.model_dump(), "is_canonical": v.file == sidecar.canonical}) for v in sidecar.versions]
    return VersionList(slug=slug, canonical=sidecar.canonical, versions=entries)


def create_version(section_dir: Path, slug: str, body: VersionCreate) -> VersionList:
    sidecar = _load_sidecar(section_dir, slug)
    if sidecar is None:
        canonical_file = f"{slug}.md"
        existing = section_dir / canonical_file
        if not existing.exists():
            raise NotFoundError(f"Poem '{slug}' not found")
        lines = len([l for l in existing.read_text(encoding="utf-8").splitlines() if l.strip()])
        sidecar = VersionSidecar(
            canonical=canonical_file,
            versions=[VersionEntry(file=canonical_file, label="Current", created=str(date.today()), lines=lines)],
        )

    # Determine base file
    source_file = body.source_file or sidecar.canonical
    source_path = section_dir / source_file
    if not source_path.exists():
        raise NotFoundError(f"Source file '{source_file}' not found")

    # Generate new variant filename
    variant_count = sum(1 for v in sidecar.versions if v.file != f"{slug}.md")
    new_filename = f"{slug}--v{variant_count + 1}.md"
    dest = section_dir / new_filename
    if dest.exists():
        raise ConflictError(f"Variant '{new_filename}' already exists")
    shutil.copy2(source_path, dest)

    lines = len([l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()])
    sidecar.versions.append(VersionEntry(
        file=new_filename,
        label=body.label,
        created=str(date.today()),
        lines=lines,
    ))
    _save_sidecar(section_dir, slug, sidecar)
    return list_versions(section_dir, slug)


def set_canonical(section_dir: Path, slug: str, body: VersionSetCanonical) -> VersionList:
    target = section_dir / body.file
    if not target.exists():
        raise NotFoundError(f"File '{body.file}' not found")
    sidecar = _load_sidecar(section_dir, slug)
    if sidecar is None:
        base = section_dir / f"{slug}.md"
        if not base.exists():
            raise NotFoundError(f"Poem '{slug}' not found")
        base_lines = len([l for l in base.read_text(encoding="utf-8").splitlines() if l.strip()])
        sidecar = VersionSidecar(
            canonical=f"{slug}.md",
            versions=[
                VersionEntry(file=f"{slug}.md", label="Current", created=str(date.today()), lines=base_lines),
            ],
        )
    sidecar = _ensure_canonical_entry(sidecar, slug, section_dir)
    previous_canonical = sidecar.canonical
    sidecar.canonical = body.file
    _save_sidecar(section_dir, slug, sidecar)
    version_list = list_versions(section_dir, slug)
    return version_list.model_copy(update={
        "previous_canonical": previous_canonical,
        "changed": previous_canonical != body.file,
    })


def resolve_save_path(section_dir: Path, slug: str, content: str) -> Path:
    """Choose the safest existing file to update for a slug.

    The minimal Studio editor only addresses poems by slug. If the canonical
    file switches while the editor still holds content from the previous file,
    writing blindly to the new canonical can clobber a different draft.
    Prefer the closest existing version by text similarity to reduce that risk.
    """
    candidates = [
        section_dir / filename
        for filename in _version_files(section_dir, slug)
        if (section_dir / filename).exists()
    ]
    if not candidates:
        raise NotFoundError(f"Poem '{slug}' not found")

    canonical = canonical_path(section_dir, slug)
    if len(candidates) == 1:
        return canonical

    ranked = sorted(
        candidates,
        key=lambda candidate: (
            SequenceMatcher(
                None,
                content,
                candidate.read_text(encoding="utf-8", errors="replace"),
            ).ratio(),
            candidate.name == canonical.name,
        ),
        reverse=True,
    )
    return ranked[0]


def resolve_canonical_paths(section_dir: Path) -> dict[str, Path]:
    """Return slug → canonical Path for all poems in the section dir.

    Used by build_service before passing to the compiler.
    """
    result: dict[str, Path] = {}
    for md in section_dir.glob("*.md"):
        if md.name.startswith("_") or "--" in md.stem:
            continue
        slug = md.stem
        sidecar = _load_sidecar(section_dir, slug)
        if sidecar is not None:
            result[slug] = canonical_path(section_dir, slug)
        else:
            result[slug] = md
    return result
