"""Regression tests for LaTeX escaping and the proof-build structural guards.

These cover bug classes that previously slipped through silently:

* ``escape_latex`` emitting LaTeX control sequences (``\\ldots{}``, ``---``)
  that a later escape pass then mangled — the unicode ellipsis once rendered as
  ``\\textbackslash\\{\\}ldots\\{\\}``.
* The scanner dropping markdown nested below the section level.
* Front matter (title page, dedication) sorting in among the body poems.
* Internal ``## I`` movement headings leaking into verse as literal ``\\#\\#``.
"""

import textwrap

import pytest

from texgraph.renderer import escape_latex, _md_inline_to_latex


# ---------------------------------------------------------------------------
# escape_latex — special characters, quotes, dashes, ellipsis, combinations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    # Special characters
    ("100% & $5 #1", r"100\% \& \$5 \#1"),
    ("a_b", r"a\_b"),
    # Brackets are braced so they are not read as optional args
    ("[note]", r"{[}note{]}"),
    # Em / en dash from unicode
    ("a—b", "a---b"),
    ("a–b", "a--b"),
    # Ellipsis: the regression case — must NOT be mangled by the escape pass
    ("Roses…the", r"Roses\ldots{}the"),
    ("Roses...the", r"Roses\ldots{}the"),
    # Ellipsis adjacent to an escaped special must stay clean
    ("50%...done", r"50\%\ldots{}done"),
    # Backslash escapes to a command, not a mangled ellipsis
    ("a\\b", r"a\textbackslash{}b"),
])
def test_escape_latex_cases(raw, expected):
    assert escape_latex(raw) == expected


def test_escape_latex_smart_quotes_around_special_char():
    # Straight quotes become TeX ligatures; the escaped content survives intact.
    assert escape_latex('say "50%" now') == r"say ``50\%'' now"


def test_escape_latex_no_double_ellipsis():
    # A unicode ellipsis already converted must not be re-collapsed.
    assert escape_latex("a…b...c") == r"a\ldots{}b\ldots{}c"


def test_escape_latex_emits_no_raw_markup():
    # No literal markdown emphasis markers survive a title-style escape.
    out = escape_latex("plain title, no markup")
    assert "*" not in out and "_" not in out


# ---------------------------------------------------------------------------
# _md_inline_to_latex — emphasis conversion
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    ("the *Book* of Nature", r"the \textit{Book} of Nature"),
    ("a **bold** word", r"a \textbf{bold} word"),
    ("***both***", r"\textbf{\textit{both}}"),
])
def test_md_inline_emphasis(raw, expected):
    assert _md_inline_to_latex(raw) == expected


# ---------------------------------------------------------------------------
# Scanner orphan-guard
# ---------------------------------------------------------------------------

def _section(dirpath, *names):
    dirpath.mkdir(parents=True, exist_ok=True)
    for n in names:
        (dirpath / n).write_text(
            "---\ntitle: 'X'\ntype: poem\norder: 1\n---\n\nA line.\n",
            encoding="utf-8",
        )


def test_scan_raises_on_orphaned_nested_markdown(tmp_path):
    from texgraph.parser import PoetryParser

    content = tmp_path / "reading"
    _section(content / "01_book", "001_poem.md")
    # A poem nested one level too deep — must be caught, not dropped.
    _section(content / "01_book" / "subgroup", "001_lost.md")

    with pytest.raises(ValueError, match="silently dropped"):
        PoetryParser().scan_collection(content)


def test_scan_accepts_flat_section(tmp_path):
    from texgraph.parser import PoetryParser

    content = tmp_path / "reading"
    _section(content / "01_book", "001_poem.md", "002_poem.md")

    sections = PoetryParser().scan_collection(content)
    assert sum(len(s.poems) for s in sections) == 2


# ---------------------------------------------------------------------------
# Front-matter ordering: title page, then dedication, then body
# ---------------------------------------------------------------------------

def test_front_matter_sorts_before_body(tmp_path):
    from texgraph.parser import PoetryParser

    content = tmp_path / "reading"
    book = content / "01_book"
    book.mkdir(parents=True)
    (book / "_title.md").write_text(
        "---\ntitle: 'The Book'\ntype: section-title\norder: 0\n---\n", encoding="utf-8")
    # Dedication shares order: 1 with the first poem — the type rank must still
    # place it ahead of the body, not sorted in among the poems.
    (book / "00_dedication.md").write_text(
        "---\ntitle: 'To X'\ntype: dedicatory-poem\norder: 1\n---\n\nA line.\n", encoding="utf-8")
    (book / "001_poem.md").write_text(
        "---\ntitle: 'First'\ntype: poem\norder: 1\n---\n\nA line.\n", encoding="utf-8")

    section = PoetryParser().scan_collection(content)[0]
    types = [p.type for p in section.poems]
    assert types == ["section-title", "dedicatory-poem", "poem"]


# ---------------------------------------------------------------------------
# Movement headings render as labels, not literal markdown
# ---------------------------------------------------------------------------

MOVEMENT_POEM = textwrap.dedent("""\
    ---
    title: 'A Song'
    type: poem
    order: 1
    ---

    ## I

    First movement line.

    ## II

    Second movement line.
""")


def test_movement_heading_becomes_label_not_verse(tmp_path):
    from texgraph.parser import PoetryParser
    from texgraph.renderer import LaTeXRenderer

    f = tmp_path / "poem.md"
    f.write_text(MOVEMENT_POEM, encoding="utf-8")
    poem = PoetryParser().parse_file(f)
    ctx = LaTeXRenderer()._process_poem(poem)

    movements = [s for s in ctx["stanzas"] if s.get("is_movement")]
    assert [m["label"] for m in movements] == ["I", "II"]
    # No stanza should carry the raw heading text as a verse line.
    for stanza in ctx["stanzas"]:
        for line in stanza["lines"]:
            assert "#" not in line
