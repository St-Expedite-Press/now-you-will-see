"""Source coverage: reading edition must cover every transcription poem 1:1."""

from pathlib import Path

import pytest

from texgraph.coverage import check_source_coverage


def _witness(poems_dir: Path, name: str) -> Path:
    poems_dir.mkdir(parents=True, exist_ok=True)
    f = poems_dir / name
    f.write_text("---\ntitle: W\n---\n\nA line.\n", encoding="utf-8")
    return f


def _reader(section: Path, name: str, source: str | None, dedication: bool = False) -> None:
    section.mkdir(parents=True, exist_ok=True)
    typ = "dedicatory-poem" if dedication else "poem"
    src = f"source: '{source}'\n" if source else ""
    (section / name).write_text(
        f"---\ntitle: R\ntype: {typ}\norder: 1\n{src}---\n\nA line.\n",
        encoding="utf-8",
    )


def _layout(tmp_path: Path) -> tuple[Path, Path]:
    """Return (repo_root, reading_dir) with a transcription poems/ dir."""
    repo = tmp_path
    poems = repo / "transcription" / "books" / "01" / "poems"
    _witness(poems, "001.md")
    _witness(poems, "002.md")
    reading = repo / "reading"
    (reading / "01_book").mkdir(parents=True)
    return repo, reading


def test_clean_bijection_is_ok(tmp_path):
    repo, reading = _layout(tmp_path)
    _reader(reading / "01_book", "001.md", "transcription/books/01/poems/001.md")
    _reader(reading / "01_book", "002.md", "transcription/books/01/poems/002.md")
    rep = check_source_coverage(reading, repo)
    assert rep.ok
    assert rep.reading_poems == 2 and rep.transcription_poems == 2


def test_unreferenced_transcription_poem_fails(tmp_path):
    repo, reading = _layout(tmp_path)
    _reader(reading / "01_book", "001.md", "transcription/books/01/poems/001.md")
    # 002 witness exists but is never referenced -> would be unbuilt
    rep = check_source_coverage(reading, repo)
    assert not rep.ok
    assert any("002.md" in u for u in rep.unreferenced)


def test_broken_source_fails(tmp_path):
    repo, reading = _layout(tmp_path)
    _reader(reading / "01_book", "001.md", "transcription/books/01/poems/001.md")
    _reader(reading / "01_book", "002.md", "transcription/books/01/poems/NOPE.md")
    rep = check_source_coverage(reading, repo)
    assert not rep.ok
    assert rep.broken_source


def test_duplicate_witness_fails(tmp_path):
    repo, reading = _layout(tmp_path)
    _reader(reading / "01_book", "001.md", "transcription/books/01/poems/001.md")
    _reader(reading / "01_book", "dup.md", "transcription/books/01/poems/001.md")
    # 002 now unreferenced too, but duplicate is the point
    rep = check_source_coverage(reading, repo)
    assert not rep.ok
    assert rep.duplicate_source


def test_dedication_without_source_is_only_a_warning(tmp_path):
    repo, reading = _layout(tmp_path)
    _reader(reading / "01_book", "001.md", "transcription/books/01/poems/001.md")
    _reader(reading / "01_book", "002.md", "transcription/books/01/poems/002.md")
    _reader(reading / "01_book", "00_dedication.md", None, dedication=True)
    rep = check_source_coverage(reading, repo)
    assert rep.ok  # dedication missing source is not a failure
    assert "00_dedication.md" not in rep.missing_source


# --- Fletcher integration: the live edition must always be complete -----------

def test_fletcher_edition_is_complete():
    from texgraph.env import repo_root

    root = repo_root()
    reading = (
        root / "projects" / "fletcher-early-works"
        / "manuscript" / "reading"
    )
    if not reading.exists():
        pytest.skip("Fletcher early-works project not present")
    rep = check_source_coverage(reading, root)
    assert rep.ok, (
        f"unreferenced={rep.unreferenced} broken={rep.broken_source} "
        f"duplicate={rep.duplicate_source}"
    )
