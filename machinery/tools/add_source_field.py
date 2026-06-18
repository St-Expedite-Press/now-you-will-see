"""Add source: field to reading-edition poem frontmatter.

Adds a relative path back to the transcription witness for every file
with type: poem or type: dedicatory-poem in manuscript/reading/.
Skips files that already have a source: field.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

READING_ROOT = REPO_ROOT / "projects/fletcher-complete-original-collections/manuscript/reading"
TRANSCRIPTION_POEMS = REPO_ROOT / "projects/fletcher-complete-original-collections/transcription/volumes/01_early_works/books"
TRANSCRIPTION_FRONT_MATTER = TRANSCRIPTION_POEMS  # each book has front_matter/ subdir

# Map reading book dir → transcription book dir
BOOK_MAP = {
    "01_the-book-of-nature": "01_the_book_of_nature_1910_1912",
    "02_the-dominant-city": "02_the_dominant_city_1911_1912",
    "03_fire-and-wine": "03_fire_and_wine",
    "04_fools-gold": "04_fools_gold",
    "05_visions-of-the-evening": "05_visions_of_the_evening",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def get_frontmatter_type(text: str) -> str | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.startswith("type:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return None


def has_source_field(text: str) -> bool:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return False
    for line in m.group(1).splitlines():
        if line.startswith("source:"):
            return True
    return False


def find_transcription_path(reading_file: Path, book_dir: str) -> Path | None:
    """Find the transcription witness for a reading-edition poem file."""
    transcription_book = BOOK_MAP.get(book_dir)
    if not transcription_book:
        return None
    book_path = TRANSCRIPTION_POEMS / transcription_book
    filename = reading_file.name

    # Try poems/ first
    candidate = book_path / "poems" / filename
    if candidate.exists():
        return candidate

    # Try front_matter/ (for dedicatory poems and other front matter)
    candidate = book_path / "front_matter" / filename
    if candidate.exists():
        return candidate

    return None


def relative_source(reading_file: Path, transcription_file: Path) -> str:
    """Return the relative path from reading_file to transcription_file."""
    return str(transcription_file.relative_to(REPO_ROOT)).replace("\\", "/")


def insert_source_field(text: str, source_value: str) -> str:
    """Insert source: field after the last existing frontmatter field."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm_content = m.group(1)
    new_fm = fm_content + f"\nsource: '{source_value}'"
    return text[:m.start(1)] + new_fm + text[m.end(1):]


def process_file(reading_file: Path) -> str:
    text = reading_file.read_text(encoding="utf-8")
    ftype = get_frontmatter_type(text)
    if ftype not in ("poem", "dedicatory-poem"):
        return "skip:not-poem"
    if has_source_field(text):
        return "skip:has-source"

    # Determine book directory (always the first book-level dir under reading/)
    parts = reading_file.relative_to(READING_ROOT).parts
    book_dir = parts[0]

    transcription_file = find_transcription_path(reading_file, book_dir)
    if transcription_file is None:
        return f"MISSING: no transcription witness found for {reading_file.relative_to(REPO_ROOT)}"

    # Path is relative to repo root (absolute-ish, consistent reference point)
    source_value = relative_source(reading_file, transcription_file)
    new_text = insert_source_field(text, source_value)
    reading_file.write_text(new_text, encoding="utf-8")
    return f"updated: {source_value}"


def main() -> None:
    updated = 0
    skipped = 0
    missing = []

    for md_file in sorted(READING_ROOT.rglob("*.md")):
        if md_file.name == "index.md":
            continue
        result = process_file(md_file)
        if result.startswith("updated"):
            updated += 1
        elif result.startswith("skip"):
            skipped += 1
        else:
            missing.append(f"  {md_file.relative_to(REPO_ROOT)}: {result}")

    print(f"Updated:  {updated}")
    print(f"Skipped:  {skipped}")
    if missing:
        print(f"Missing ({len(missing)}):")
        for m in missing:
            print(m)
    else:
        print("Missing:  0")


if __name__ == "__main__":
    main()
