"""Source coverage: prove every transcription poem reaches the reading edition.

A reading-edition poem links to its documentary witness through its ``source:``
front-matter field.  This module checks the mapping is a clean bijection — every
reading poem points at a real transcription file, no two reading poems share a
witness, and no transcription poem is left unbuilt.  It exists because an entire
poem sequence once vanished silently; this turns "did we lose a poem?" into a
deterministic, testable answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

# Section-level files that are not poems.
_SKIP_NAMES = {"index.md"}


@dataclass
class CoverageReport:
    """Result of a reading↔transcription coverage check."""

    reading_poems: int = 0
    transcription_poems: int = 0
    missing_source: list[str] = field(default_factory=list)   # poem files with no source:
    broken_source: list[str] = field(default_factory=list)    # source: points nowhere
    duplicate_source: list[str] = field(default_factory=list) # one witness, many readers
    unreferenced: list[str] = field(default_factory=list)     # transcription poem never built

    @property
    def ok(self) -> bool:
        """True when the mapping is a clean bijection (warnings aside).

        ``missing_source`` is a warning, not a failure: dedications and other
        front matter legitimately have no poem witness.
        """
        return not (self.broken_source or self.duplicate_source or self.unreferenced)

    @property
    def problems(self) -> int:
        return len(self.broken_source) + len(self.duplicate_source) + len(self.unreferenced)


def _poem_files(reading_dir: Path) -> list[Path]:
    """Reading-edition poem files: section .md files, excluding nav/meta/title."""
    out: list[Path] = []
    for section in sorted(
        p for p in reading_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    ):
        for f in sorted(section.glob("*.md")):
            if f.name in _SKIP_NAMES or f.name.startswith("_"):
                continue
            out.append(f)
    return out


def _is_dedication(meta: dict) -> bool:
    return str(meta.get("type", "")).lower().startswith("dedicat")


def check_source_coverage(reading_dir: Path, repo_root: Path) -> CoverageReport:
    """Check that the reading edition covers its transcription witnesses 1:1.

    Parameters
    ----------
    reading_dir:
        The ``manuscript/reading`` directory whose poems carry ``source:`` fields.
    repo_root:
        Repository root used to resolve repo-relative ``source:`` paths.
    """
    rep = CoverageReport()
    referenced: dict[Path, list[str]] = {}

    poem_files = _poem_files(reading_dir)
    rep.reading_poems = len(poem_files)

    for f in poem_files:
        meta = frontmatter.load(str(f)).metadata
        src = str(meta.get("source") or "").strip()
        if not src:
            if not _is_dedication(meta):
                rep.missing_source.append(f.name)
            continue
        resolved = (repo_root / src).resolve()
        if not resolved.is_file():
            rep.broken_source.append(f"{f.name} -> {src}")
            continue
        referenced.setdefault(resolved, []).append(f.name)

    for witness, readers in sorted(referenced.items()):
        if len(readers) > 1:
            rep.duplicate_source.append(f"{witness.name} <- {', '.join(readers)}")

    # Completeness applies to transcription poems only: every file in a referenced
    # ``poems/`` directory must be built.  Front-matter witnesses (a dedication's
    # source, imprints, colophons) are link-checked but not required wholesale.
    witness_dirs = {w.parent for w in referenced if w.parent.name == "poems"}
    all_witnesses: set[Path] = set()
    for d in witness_dirs:
        for t in d.glob("*.md"):
            if t.name in _SKIP_NAMES or t.name.startswith("_"):
                continue
            all_witnesses.add(t.resolve())
    rep.transcription_poems = len(all_witnesses)

    for witness in sorted(all_witnesses):
        if witness not in referenced:
            rep.unreferenced.append(str(witness))

    return rep
