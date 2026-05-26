"""
Jinja2-based LaTeX renderer for Texgraph.

Loads templates from the ``templates/`` directory bundled with the package
(or from a user-supplied override directory) and renders the full ``.tex``
document string from assembled collection data.

Typical usage::

    from texgraph.renderer import LaTeXRenderer
    from texgraph.config import CollectionConfig
    from texgraph.parser import PoetryParser

    config = CollectionConfig.from_yaml("collection.yaml")
    parser = PoetryParser()
    sections = parser.scan_collection(config.resolved_content_dir)

    renderer = LaTeXRenderer()
    tex_source = renderer.render(
        collection_data={"config": config.as_dict(), "sections": sections},
        template_name="collection.tex.jinja2",
    )
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    select_autoescape,
)

from texgraph.parser import CyclePart, Poem, Scene, Section, Stanza


# ---------------------------------------------------------------------------
# LaTeX character escaping
# ---------------------------------------------------------------------------

# Ordered so that backslash is replaced first (it is the escape char itself)
_LATEX_ESCAPE_MAP: list[tuple[str, str]] = [
    ("\\", r"\textbackslash{}"),
    ("&",  r"\&"),
    ("%",  r"\%"),
    ("$",  r"\$"),
    ("#",  r"\#"),
    ("_",  r"\_"),
    ("{",  r"\{"),
    ("}",  r"\}"),
    ("~",  r"\textasciitilde{}"),
    ("^",  r"\textasciicircum{}"),
    ("[",  r"{[}"),
    ("]",  r"{]}"),
]

# Fancy quotes — only convert straight ASCII double-quote pairs.
# Unicode curly single/double quotes are handled in _DASH_MAP above.
# Single-quote pairs are NOT converted here because the regex greedily
# matches apostrophes in contractions (e.g. "don't") against later
# TeX ligatures, producing corrupted output.
_SMART_QUOTE_MAP: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'"([^"]+)"'), r"``\1''"),   # "word" → ``word''
]

# Em-dash, en-dash, ellipsis, and Unicode curly quote replacements
_DASH_MAP: list[tuple[str, str]] = [
    ("—", "---"),
    ("–", "--"),
    ("…", r"\ldots{}"),
    ("\u201c", "``"),   # left double quotation mark → ``
    ("\u201d", "''"),   # right double quotation mark → ''
    ("\u2018", "`"),    # left single quotation mark → `
    ("\u2019", "'"),    # right single quotation mark → '
]


def escape_latex(text: str, *, smart_quotes: bool = True) -> str:
    """Escape *text* so it is safe to embed in a LaTeX document.

    Handles:

    * Special LaTeX characters (``& % $ # _ { } ~ ^`` and ``\\``)
    * Smart/curly quotes → TeX quote ligatures
    * Em-dash, en-dash, ellipsis

    Parameters
    ----------
    text:
        Raw string to escape.
    smart_quotes:
        When ``True`` (default), convert Unicode curly quotes and straight
        double/single quotes to TeX ligature pairs before the escape pass.

    Returns
    -------
    str
        LaTeX-safe string.
    """
    if smart_quotes:
        for pattern, replacement in _SMART_QUOTE_MAP:
            text = pattern.sub(replacement, text)

    for original, replacement in _DASH_MAP:
        text = text.replace(original, replacement)

    for original, replacement in _LATEX_ESCAPE_MAP:
        text = text.replace(original, replacement)

    return text


# ---------------------------------------------------------------------------
# Inline markdown → LaTeX conversion (used for screenplay lines)
# ---------------------------------------------------------------------------

# Matches ***bold-italic***, **bold**, *italic*, _italic_ — longest first
_MD_INLINE_RE = re.compile(r"\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|_(.+?)_")


def _md_inline_to_latex(text: str) -> str:
    """Convert inline markdown emphasis to LaTeX, escaping plain-text portions.

    Processes ``**bold**``, ``*italic*``, ``_italic_``, and ``***bold-italic***``
    in the text.  Plain text between/around spans is passed through
    :func:`escape_latex`.  The LaTeX command strings themselves are constructed
    directly and are never re-escaped.

    Parameters
    ----------
    text:
        A single line that may contain markdown inline markup.

    Returns
    -------
    str
        LaTeX-safe string with emphasis converted to ``\\textbf{}``,
        ``\\textit{}``, or ``\\textbf{\\textit{}}``.
    """
    result: list[str] = []
    last_end = 0
    for m in _MD_INLINE_RE.finditer(text):
        result.append(escape_latex(text[last_end:m.start()]))
        g1, g2, g3, g4 = m.group(1), m.group(2), m.group(3), m.group(4)
        if g1 is not None:
            result.append(r"\textbf{\textit{" + escape_latex(g1) + r"}}")
        elif g2 is not None:
            result.append(r"\textbf{" + escape_latex(g2) + r"}")
        else:
            inner = g3 if g3 is not None else (g4 or "")
            result.append(r"\textit{" + escape_latex(inner) + r"}")
        last_end = m.end()
    result.append(escape_latex(text[last_end:]))
    return "".join(result)


# ---------------------------------------------------------------------------
# Jinja2 environment helpers
# ---------------------------------------------------------------------------

def _build_env(template_dirs: list[Path]) -> Environment:
    """Create a Jinja2 :class:`~jinja2.Environment` configured for LaTeX output.

    * Uses ``\\BLOCK{}``, ``\\VAR{}``, ``\\#`` delimiters so Jinja2 syntax
      does not collide with LaTeX syntax.
    * Registers :func:`escape_latex` as a filter and global.
    * ``StrictUndefined`` ensures template bugs surface as clear errors.
    """
    loader = FileSystemLoader([str(d) for d in template_dirs], encoding="utf-8")

    env = Environment(
        loader=loader,
        # Use LaTeX-friendly block/variable delimiters
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=select_autoescape(enabled_extensions=()),  # no HTML escaping
        undefined=StrictUndefined,
    )

    # Register custom filters
    env.filters["latex"] = escape_latex
    env.filters["latex_noquotes"] = lambda t: escape_latex(t, smart_quotes=False)

    # Register helper globals
    env.globals["escape_latex"] = escape_latex

    return env


# ---------------------------------------------------------------------------
# Renderer class
# ---------------------------------------------------------------------------

_BUILTIN_TEMPLATES_DIR = Path(__file__).parent / "templates"


class LaTeXRenderer:
    """Render a full LuaLaTeX document from parsed collection data.

    Parameters
    ----------
    extra_template_dirs:
        Additional directories to search for templates *before* the built-in
        ``templates/`` directory.  Useful for user-supplied template overrides.
    """

    def __init__(self, extra_template_dirs: list[Path] | None = None) -> None:
        dirs: list[Path] = list(extra_template_dirs or [])
        dirs.append(_BUILTIN_TEMPLATES_DIR)
        self._env = _build_env(dirs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(
        self,
        collection_data: dict[str, Any],
        template_name: str = "collection.tex.jinja2",
    ) -> str:
        """Render the full ``.tex`` document string.

        Parameters
        ----------
        collection_data:
            A dict containing at minimum:

            * ``"config"`` — output of :meth:`~texgraph.config.CollectionConfig.as_dict`
            * ``"sections"`` — list of :class:`~texgraph.parser.Section` objects

        template_name:
            Name of the Jinja2 template file to use.  Must be findable in
            one of the template directories.

        Returns
        -------
        str
            The rendered LaTeX source as a string.
        """
        template = self._env.get_template(template_name)
        ctx = self._build_context(collection_data)
        return template.render(**ctx)

    def render_poem(self, poem: Poem, template_name: str = "poem.tex.jinja2") -> str:
        """Render a single poem fragment (useful for previewing / testing).

        Parameters
        ----------
        poem:
            A parsed :class:`~texgraph.parser.Poem`.
        template_name:
            Template to use for the poem fragment.

        Returns
        -------
        str
            Rendered LaTeX fragment.
        """
        template = self._env.get_template(template_name)
        return template.render(poem=self._process_poem(poem), escape_latex=escape_latex)

    # ------------------------------------------------------------------
    # Context construction
    # ------------------------------------------------------------------

    def _build_context(self, collection_data: dict[str, Any]) -> dict[str, Any]:
        """Build the full Jinja2 template context from *collection_data*.

        Enriches the raw data with pre-processed, escaped versions of all
        metadata strings so that templates can use ``\\VAR{config.title}``
        without worrying about escaping.
        """
        config: dict[str, Any] = collection_data.get("config", {})
        sections: list[Section] = collection_data.get("sections", [])

        escaped_config = {
            k: (
                dict(v)
                if k == "render_config" and isinstance(v, dict)
                else {rk: escape_latex(str(rv), smart_quotes=False) if isinstance(rv, str) else rv for rk, rv in v.items()}
                if isinstance(v, dict)
                else escape_latex(str(v)) if isinstance(v, str) else v
            )
            for k, v in config.items()
        }

        processed_sections = [self._process_section(s) for s in sections]

        return {
            "config": escaped_config,
            "sections": processed_sections,
            "raw_config": config,
            "escape_latex": escape_latex,
        }

    def _process_section(self, section: Section) -> dict[str, Any]:
        """Convert a :class:`~texgraph.parser.Section` into a template-friendly dict."""
        return {
            "title": escape_latex(section.title),
            "meta": {k: escape_latex(str(v)) if isinstance(v, str) else v
                     for k, v in section.meta.items()},
            "poems": [self._process_poem(p) for p in section.poems],
        }

    def _process_poem(self, poem: Poem) -> dict[str, Any]:
        """Convert a :class:`~texgraph.parser.Poem` into a template-friendly dict.

        Handles three block types:

        * **poem**: stanzas rendered as verse environments; each line escaped
          individually with ``\\\\`` line-break except at stanza boundaries.
        * **prose**: body joined as a single block; lines joined with a space,
          stanza boundaries become ``\\par``.
        * **poem-cycle**: ``parts`` list populated; each part contains its own
          ``title`` and ``stanzas``; ``stanzas`` at the top level is empty.
        """
        if poem.is_cycle:
            rendered_stanzas: list[list[str]] = []
            rendered_parts = self._render_cycle_parts(poem.parts)
            rendered_scenes: list[dict[str, Any]] = []
        elif poem.is_screenplay:
            rendered_stanzas = []
            rendered_parts = []
            rendered_scenes = self._render_screenplay(poem.scenes)
        elif poem.type == "prose":
            rendered_stanzas = self._render_prose(poem.stanzas)
            rendered_parts = []
            rendered_scenes = []
        else:
            rendered_stanzas = self._render_poem_stanzas(poem.stanzas)
            rendered_parts = []
            rendered_scenes = []

        return {
            "title": escape_latex(poem.title),
            "subtitle": escape_latex(poem.subtitle),
            "type": poem.type,
            "is_cycle": poem.is_cycle,
            "is_screenplay": poem.is_screenplay,
            "cycle": escape_latex(poem.cycle),
            "cycle_part": poem.cycle_part,
            "epigraph": escape_latex(poem.epigraph),
            "epigraph_author": escape_latex(str(poem.meta.get("epigraph_author", ""))),
            "dedication": escape_latex(poem.dedication),
            "render_config": dict(poem.meta.get("render_config") or {}),
            "meta": {k: escape_latex(str(v)) if isinstance(v, str) else v
                     for k, v in poem.meta.items()},
            "stanzas": rendered_stanzas,
            "parts": rendered_parts,
            "scenes": rendered_scenes,
            "path": str(poem.path),
        }

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render_cycle_parts(self, parts: list[CyclePart]) -> list[dict[str, Any]]:
        """Render a list of :class:`~texgraph.parser.CyclePart` objects.

        Each part is converted to a dict with:

        * ``"title"`` — LaTeX-escaped part title (e.g. ``"I. That's How It Is"``)
        * ``"stanzas"`` — list of stanza line-lists, same format as
          :meth:`_render_poem_stanzas`
        """
        result: list[dict[str, Any]] = []
        for part in parts:
            result.append({
                "title": escape_latex(part.title),
                "stanzas": self._render_poem_stanzas(part.stanzas),
            })
        return result

    def _render_screenplay(self, scenes: list[Scene]) -> list[dict[str, Any]]:
        """Render screenplay scenes to template-friendly dicts.

        Each scene becomes a dict with a ``"stanzas"`` list.  Every stanza
        dict contains:

        * ``"lines"`` — inline-markdown-converted, LaTeX-escaped lines.
          Non-last lines are suffixed with ``\\\\`` for verse line-breaks.
        * ``"is_blockquote"`` — ``True`` when every non-empty line begins
          with ``"> "`` (markdown block-quote prefix), used by the template
          to wrap the stanza in ``\\begin{quote}\\itshape``.
        """
        result: list[dict[str, Any]] = []
        for scene in scenes:
            rendered_stanzas: list[dict[str, Any]] = []
            for stanza in scene.stanzas:
                non_empty = [l for l in stanza.lines if l.strip()]
                is_blockquote = bool(non_empty) and all(
                    l.startswith(">") for l in non_empty
                )
                rendered_lines: list[str] = []
                for i, line in enumerate(stanza.lines):
                    if is_blockquote:
                        raw = line[2:] if line.startswith("> ") else line[1:]
                    else:
                        raw = line
                    escaped = _md_inline_to_latex(raw.rstrip())
                    if i < len(stanza.lines) - 1:
                        escaped += r" \\"
                    rendered_lines.append(escaped)
                rendered_stanzas.append({
                    "lines": rendered_lines,
                    "is_blockquote": is_blockquote,
                })
            result.append({"stanzas": rendered_stanzas})
        return result

    @staticmethod
    def _render_poem_stanzas(stanzas: list[Stanza]) -> list[dict[str, Any]]:
        """Return a list of stanza dicts, each containing ``lines`` and ``is_blockquote``.

        A stanza is detected as a blockquote when every non-empty line begins
        with ``">"`` (the markdown blockquote prefix, with or without a
        trailing space).  The prefix is stripped before inline-markdown
        conversion.  Non-last lines within a stanza receive a ``\\\\`` suffix
        for LaTeX line-break handling.
        """
        result: list[dict[str, Any]] = []
        for stanza in stanzas:
            non_empty = [l for l in stanza.lines if l.strip()]
            is_blockquote = bool(non_empty) and all(
                l.startswith(">") for l in non_empty
            )
            rendered_lines: list[str] = []
            for i, line in enumerate(stanza.lines):
                if is_blockquote:
                    raw = line[2:] if line.startswith("> ") else line[1:]
                else:
                    raw = line
                esc = _md_inline_to_latex(raw.rstrip())
                if i < len(stanza.lines) - 1:
                    esc += r" \\"
                rendered_lines.append(esc)
            result.append({"lines": rendered_lines, "is_blockquote": is_blockquote})
        return result

    @staticmethod
    def _render_prose(stanzas: list[Stanza]) -> list[list[str]]:
        """Return prose stanzas: each stanza becomes a single joined string.

        Lines within a stanza are joined with a space; stanza boundaries
        translate to paragraph breaks (``\\par``) in the template.
        """
        result: list[list[str]] = []
        for stanza in stanzas:
            joined = " ".join(_md_inline_to_latex(line) for line in stanza.lines if line.strip())
            result.append([joined])
        return result
