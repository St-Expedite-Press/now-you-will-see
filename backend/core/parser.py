"""
Markdown/YAML front-matter parser for Texgraph poetry collections.

Directory layout expected under ``content_dir``::

    content/
        00_front/
            _section.yaml        # optional section metadata
            dedication.md
        01_poems/
            _section.yaml
            sonnet_i.md
            sonnet_ii.md
        02_notes/
            notes.md

Each ``.md`` file may have YAML front matter::

    ---
    title: "Sonnet I"
    type: poem          # poem | prose | poem-cycle  (default: poem)
    order: 1            # explicit ordering within section (optional)
    subtitle: "..."     # parenthetical subtitle or source note, e.g. "(A Cameo From Catullus)"
    epigraph: "..."
    dedication: "..."
    cycle: "..."        # name of a multi-file cycle this poem belongs to
    cycle_part: 1       # position within that cycle (1-based)
    ---

    First stanza line one
    First stanza line two

    Second stanza line one

Stanzas are separated by blank lines; lines within a stanza are kept intact.

Poem Cycles
-----------
Two formats are supported:

**Single-file cycle** (``type: poem-cycle`` or ``type: poem cycle``):
The body contains multiple sub-poems delimited by ``###`` headings::

    ---
    title: "Cycle Title"
    type: poem-cycle
    order: 3
    ---

    ### I. First Sub-poem

    Line one
    Line two

    ### II. Second Sub-poem

    Line one

The ``##`` heading level (if present) is treated as a decorative title
repeat and skipped during parsing.

**Multi-file linked cycle** (individual poems with a shared ``cycle`` field):
Each poem carries ``cycle: "Shared Cycle Name"`` and optionally
``cycle_part: N`` for explicit ordering within the cycle.  The renderer
groups consecutive poems that share the same ``cycle`` value and renders
them as a numbered sequence under a shared heading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter  # python-frontmatter
import yaml


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Stanza:
    """A single stanza: an ordered list of lines."""
    lines: list[str] = field(default_factory=list)


@dataclass
class CyclePart:
    """One sub-poem within a single-file poem cycle.

    Attributes
    ----------
    title:
        The heading text of this sub-poem (markdown emphasis stripped).
    stanzas:
        Stanzas parsed from this sub-poem's body text.
    """
    title: str
    stanzas: list[Stanza] = field(default_factory=list)


@dataclass
class Scene:
    """One scene within a poem-screenplay, delimited by ``---`` scene breaks.

    Attributes
    ----------
    stanzas:
        Stanzas of lines (dialogue, stage directions, etc.) within this scene.
    """
    stanzas: list[Stanza] = field(default_factory=list)


@dataclass
class Poem:
    """A parsed poem, prose piece, or poem cycle with its metadata and stanzas.

    For regular poems and prose, ``stanzas`` holds the content and ``parts``
    is empty.  For single-file cycles (``type: poem-cycle``), ``parts`` holds
    the individual :class:`CyclePart` objects and ``stanzas`` is empty.
    """

    path: Path
    meta: dict[str, Any]
    stanzas: list[Stanza]
    parts: list[CyclePart] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)

    # Convenience accessors ---------------------------------------------------

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.path.stem.replace("_", " ").title())

    @property
    def type(self) -> str:
        """Normalised type string.

        Recognised values: ``'poem'``, ``'prose'``, ``'poem-cycle'``,
        ``'poem-screenplay'``.
        The legacy value ``'poem cycle'`` (with space) is normalised to
        ``'poem-cycle'``.
        """
        raw = str(self.meta.get("type", "poem")).lower().strip()
        if raw == "poem cycle":
            return "poem-cycle"
        if raw == "prose-poem":
            return "prose"
        return raw

    @property
    def is_cycle(self) -> bool:
        """True when this file is a single-file poem cycle."""
        return self.type == "poem-cycle"

    @property
    def is_screenplay(self) -> bool:
        """True when this file is a poem-screenplay interlude."""
        return self.type == "poem-screenplay"

    @property
    def order(self) -> int:
        """Explicit ordering key; falls back to 9999 if not set."""
        try:
            return int(self.meta.get("order", 9999))
        except (TypeError, ValueError):
            return 9999

    @property
    def subtitle(self) -> str:
        """Parenthetical subtitle or source note, e.g. ``'(A Cameo From Catullus)'``."""
        return str(self.meta.get("subtitle", ""))

    @property
    def epigraph(self) -> str:
        return str(self.meta.get("epigraph", ""))

    @property
    def dedication(self) -> str:
        return str(self.meta.get("dedication", ""))

    @property
    def cycle(self) -> str:
        """Name of the multi-file cycle this poem belongs to, or empty string."""
        return str(self.meta.get("cycle", ""))

    @property
    def cycle_part(self) -> int:
        """Position within a multi-file cycle (1-based); 0 if not set."""
        try:
            return int(self.meta.get("cycle_part", 0))
        except (TypeError, ValueError):
            return 0

    @property
    def raw_lines(self) -> list[str]:
        """Flat list of every line across all stanzas (without blank separators)."""
        result: list[str] = []
        for stanza in self.stanzas:
            result.extend(stanza.lines)
        return result


@dataclass
class Section:
    """A directory-level section of the collection."""

    path: Path
    meta: dict[str, Any]
    poems: list[Poem] = field(default_factory=list)

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.path.name.lstrip("0123456789_- ").replace("_", " ").title())

    @property
    def order(self) -> int:
        """Derived from the numeric prefix in the directory name (e.g. ``01_poems`` → 1)."""
        try:
            return int(self.meta.get("order", _numeric_prefix(self.path.name)))
        except (TypeError, ValueError):
            return 9999


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BLANK_LINE_RE = re.compile(r"^\s*$")
# Matches a ### sub-poem heading (and optionally ## title-repeat headings)
_CYCLE_PART_RE = re.compile(r"^###\s+(.+)$", re.MULTILINE)
# Strip markdown emphasis markers ( *text*, **text**, _text_, ***text*** )
_MD_EMPHASIS_RE = re.compile(r"[\*_]{1,3}(.*?)[\*_]{1,3}")
# Matches a scene break: a line containing only --- (with optional surrounding whitespace)
_SCENE_BREAK_RE = re.compile(r"^\s*---\s*$", re.MULTILINE)


def _numeric_prefix(name: str) -> int:
    """Extract a leading integer from a string like ``'01_poems'``."""
    m = re.match(r"^(\d+)", name)
    return int(m.group(1)) if m else 9999


def _strip_md_emphasis(text: str) -> str:
    """Remove ``*``, ``**``, ``_``, ``***`` markers, keeping inner text."""
    return _MD_EMPHASIS_RE.sub(r"\1", text).strip()


def _split_cycle_parts(body: str) -> list[CyclePart]:
    """Split a poem-cycle body into :class:`CyclePart` objects.

    Sub-poems are delimited by ``###`` headings.  ``##``-level headings
    (decorative title repeats) are silently skipped.  Markdown emphasis
    markers in heading text are stripped.

    Parameters
    ----------
    body:
        Raw body text of a cycle file (after front-matter removal).

    Returns
    -------
    list[CyclePart]
        One :class:`CyclePart` per ``###`` heading found, in document order.
        Returns a single empty-titled part if no ``###`` headings are present
        (graceful fallback for files in transition).
    """
    headings = list(_CYCLE_PART_RE.finditer(body))

    if not headings:
        # No ### headings — treat the whole body as one unnamed part
        return [CyclePart(title="", stanzas=_split_stanzas(body.strip()))]

    parts: list[CyclePart] = []

    # Preamble: content that appears before the first ### heading
    preamble = body[:headings[0].start()].strip()
    if preamble:
        parts.append(CyclePart(title="", stanzas=_split_stanzas(preamble)))

    for i, match in enumerate(headings):
        raw_title = match.group(1).strip()
        title = _strip_md_emphasis(raw_title)

        # Content runs from end of this heading to start of the next (or EOF)
        content_start = match.end()
        content_end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        content = body[content_start:content_end].strip()

        parts.append(CyclePart(title=title, stanzas=_split_stanzas(content)))

    return parts


def _split_scenes(body: str) -> list[Scene]:
    """Split a poem-screenplay body into :class:`Scene` objects on ``---`` breaks.

    Parameters
    ----------
    body:
        Raw body text of a poem-screenplay file (after front-matter removal).

    Returns
    -------
    list[Scene]
        One :class:`Scene` per segment between ``---`` scene breaks.
    """
    raw_parts = _SCENE_BREAK_RE.split(body)
    scenes: list[Scene] = []
    for raw in raw_parts:
        raw = raw.strip()
        if raw:
            scenes.append(Scene(stanzas=_split_stanzas(raw)))
    return scenes


def _split_stanzas(body: str) -> list[Stanza]:
    """Split raw markdown body text into a list of :class:`Stanza` objects.

    Stanzas are delimited by one or more blank lines.  Each stanza is a
    sequence of non-blank lines.  Trailing whitespace is stripped from every
    line.

    Parameters
    ----------
    body:
        The raw markdown body (everything after the front-matter block).

    Returns
    -------
    list[Stanza]
        Ordered list of stanzas; guaranteed to be non-empty (may contain a
        single stanza with a single empty string if *body* is blank).
    """
    stanzas: list[Stanza] = []
    current: list[str] = []

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if _BLANK_LINE_RE.match(line):
            if current:
                stanzas.append(Stanza(lines=current))
                current = []
        else:
            current.append(line)

    if current:
        stanzas.append(Stanza(lines=current))

    # Guarantee at least one stanza so callers never deal with empty lists
    if not stanzas:
        stanzas.append(Stanza(lines=[""]))

    return stanzas


def _load_section_meta(section_dir: Path) -> dict[str, Any]:
    """Read the optional ``_meta.yaml`` (or legacy ``_section.yaml``) inside a section directory."""
    yaml_file = section_dir / "_meta.yaml"
    if not yaml_file.exists():
        yaml_file = section_dir / "_section.yaml"  # legacy fallback
    if not yaml_file.exists():
        return {}
    import yaml  # noqa: PLC0415 — lazy import to keep top-level clean
    with yaml_file.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _load_version_sidecar(section_dir: Path, slug: str) -> dict[str, Any]:
    """Read .slug.versions.yaml if present."""
    sidecar = section_dir / f".{slug}.versions.yaml"
    if not sidecar.exists():
        return {}
    with sidecar.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _canonical_poem_path(section_dir: Path, base_path: Path) -> Path:
    """Resolve the canonical file for a poem slug, defaulting to the base file."""
    sidecar = _load_version_sidecar(section_dir, base_path.stem)
    canonical_name = str(sidecar.get("canonical") or base_path.name)
    candidate = section_dir / canonical_name
    return candidate if candidate.is_file() else base_path


# Front-matter unit types sort ahead of body poems within a section, in this
# order.  Anything not listed is body content and sorts after (rank 2).
_FRONT_MATTER_RANK: dict[str, int] = {
    "section-title": 0,
    "dedicatory-poem": 1,
    "dedication": 1,
}


def _front_matter_rank(poem_type: str) -> int:
    """Sort rank for a unit type: 0 = title page, 1 = dedication, 2 = body."""
    return _FRONT_MATTER_RANK.get(poem_type, 2)


def _assert_no_orphaned_markdown(content_dir: Path, sub_dirs: list[Path]) -> None:
    """Raise if any ``.md`` lives below the section level and would be dropped.

    The scanner treats only immediate subdirectories of *content_dir* as
    sections, and only the ``.md`` files directly inside a section are typeset.
    A ``.md`` nested one level deeper (``section/group/poem.md``) is silently
    unreachable.  Surfacing it as an error turns a vanished-content bug into an
    actionable failure that names the offending files.
    """
    orphans: list[Path] = []
    for sub_dir in sub_dirs:
        for child in sub_dir.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                orphans.extend(sorted(child.rglob("*.md")))
    if orphans:
        rel = "\n  ".join(str(p.relative_to(content_dir)) for p in orphans)
        raise ValueError(
            f"{len(orphans)} markdown file(s) are nested below the section level "
            f"in {content_dir} and would be silently dropped from the build. "
            f"Move them up into their section directory (content is flat within "
            f"a section), or split the group into its own top-level section:\n  "
            f"{rel}"
        )


def _section_markdown_files(section_dir: Path) -> list[Path]:
    """Return section markdown files, resolving canonical versions and skipping variants."""
    resolved: list[Path] = []
    seen: set[Path] = set()

    for path in sorted(section_dir.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.suffix != ".md":
            continue
        if path.name.startswith("."):
            continue
        if path.name.startswith("_"):
            if path.name == "_title.md":
                resolved.append(path)
            continue
        if "--" in path.stem:
            continue

        canonical_path = _canonical_poem_path(section_dir, path)
        if canonical_path not in seen:
            resolved.append(canonical_path)
            seen.add(canonical_path)

    return resolved


# ---------------------------------------------------------------------------
# Main parser class
# ---------------------------------------------------------------------------

_READING_SECTION_RE = re.compile(
    r"^## (Original Lineation|Editorial Relineation|Context Notes)[ \t]*$",
    re.MULTILINE,
)


def _split_reading_sections(body: str) -> tuple[str, str]:
    """Split a reading-edition poem body into typeset text and context notes.

    Reading-edition files (see the project's manuscript EDITORIAL_PROCEDURE.md)
    hold up to three literal H2 sections: ``Original Lineation`` (the
    documentary witness), ``Editorial Relineation`` (line- and stanza-break
    decisions only), and ``Context Notes`` (editorial prose).  The Editorial
    Relineation is typeset when present, else the Original Lineation; Context
    Notes are returned separately for apparatus use and never typeset inline.
    Section boundaries are these three literal headings only — any other
    heading (e.g. a poem's internal ``## I`` movements) stays inside its
    section.  Bodies without the section headings pass through unchanged.
    """
    matches = list(_READING_SECTION_RE.finditer(body))
    if not matches:
        return body, ""
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.setdefault(m.group(1), body[m.end():end].strip("\n"))
    text = sections.get("Editorial Relineation") or sections.get("Original Lineation")
    notes = sections.get("Context Notes", "")
    if text is None:
        return body, notes
    return text, notes


class PoetryParser:
    """Parse individual poem files and whole collection directory trees.

    Parameters
    ----------
    strip_html_comments:
        When ``True`` (default), HTML comments (``<!-- ... -->``) are removed
        from the markdown body before stanza splitting.
    """

    def __init__(self, *, strip_html_comments: bool = True) -> None:
        self._strip_html_comments = strip_html_comments
        self._html_comment_re = re.compile(r"<!--.*?-->", re.DOTALL)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_file(self, path: str | Path) -> Poem:
        """Parse a single Markdown poem file.

        Parameters
        ----------
        path:
            Path to the ``.md`` file.

        Returns
        -------
        Poem
            A :class:`Poem` dataclass with ``meta`` (front-matter dict),
            ``stanzas`` (list of :class:`Stanza`), and helper properties.

        Raises
        ------
        FileNotFoundError
            If *path* does not exist.
        ValueError
            If the file cannot be decoded as UTF-8.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Poem file not found: {path}")

        try:
            post = frontmatter.load(str(path))
        except Exception as exc:
            raise ValueError(f"Failed to parse front matter in {path}: {exc}") from exc

        body: str = post.content or ""
        if self._strip_html_comments:
            body = self._html_comment_re.sub("", body)

        body, context_notes = _split_reading_sections(body)

        meta: dict[str, Any] = dict(post.metadata)
        if context_notes:
            meta.setdefault("context_notes", context_notes)

        # Detect type early (before Poem construction) so we can choose
        # the right parsing strategy.
        raw_type = str(meta.get("type", "poem")).lower().strip()
        is_cycle = raw_type in ("poem-cycle", "poem cycle")
        is_screenplay = raw_type == "poem-screenplay"

        if is_cycle:
            stanzas = []
            parts = _split_cycle_parts(body)
            scenes = []
        elif is_screenplay:
            stanzas = []
            parts = []
            scenes = _split_scenes(body)
        else:
            stanzas = _split_stanzas(body)
            parts = []
            scenes = []

        return Poem(path=path, meta=meta, stanzas=stanzas, parts=parts, scenes=scenes)

    def scan_collection(self, content_dir: str | Path) -> list[Section]:
        """Walk *content_dir* and return an ordered list of :class:`Section` objects.

        Only immediate subdirectories of *content_dir* are treated as sections.
        ``.md`` files directly inside *content_dir* (not in a subdirectory) are
        placed into an implicit ``"_root"`` section with order 0.

        Within each section, poems are sorted first by the ``order`` front-matter
        key, then alphabetically by filename.

        Parameters
        ----------
        content_dir:
            Root content directory (e.g. ``"content/"``).

        Returns
        -------
        list[Section]
            Sections sorted by their numeric directory prefix (or ``order``
            metadata key), each containing an ordered list of parsed poems.
        """
        content_dir = Path(content_dir)
        if not content_dir.exists():
            raise FileNotFoundError(f"Content directory not found: {content_dir}")

        sections: list[Section] = []

        # -- Root-level .md files -------------------------------------------
        root_poems = sorted(
            path
            for path in content_dir.glob("*.md")
            if not path.name.startswith(".") and "--" not in path.stem
        )
        if root_poems:
            section = Section(
                path=content_dir,
                meta={"title": "", "order": 0},
            )
            for md_path in root_poems:
                section.poems.append(self.parse_file(md_path))
            sections.append(section)

        # -- Sub-directory sections -----------------------------------------
        sub_dirs = sorted(
            (d for d in content_dir.iterdir() if d.is_dir() and not d.name.startswith(".")),
            key=lambda d: (_numeric_prefix(d.name), d.name),
        )

        # Guard against silently dropped content.  Only the section directory's
        # own ``.md`` files are typeset; anything nested a further level down is
        # unreachable and would vanish from the book without a trace (this is
        # exactly how an entire poem sequence once went missing).  Fail loudly.
        _assert_no_orphaned_markdown(content_dir, sub_dirs)

        for sub_dir in sub_dirs:
            meta = _load_section_meta(sub_dir)
            section = Section(path=sub_dir, meta=meta)

            md_files = _section_markdown_files(sub_dir)
            parsed: list[Poem] = [self.parse_file(f) for f in md_files]
            # Sort front matter (title page, then dedication) ahead of the body,
            # then by explicit order key, then filename.  The type rank prevents
            # a dedication with ``order: 1`` from sorting in among the poems.
            parsed.sort(key=lambda p: (_front_matter_rank(p.type), p.order, p.path.name))
            section.poems = parsed

            sections.append(section)

        # Final sort to ensure section ordering is correct after metadata overrides
        sections.sort(key=lambda s: (s.order, s.path.name))

        return sections

    # ------------------------------------------------------------------
    # Internal helpers (public for testing convenience)
    # ------------------------------------------------------------------

    @staticmethod
    def split_stanzas(body: str) -> list[Stanza]:
        """Public wrapper around :func:`_split_stanzas` for testing and external use."""
        return _split_stanzas(body)
