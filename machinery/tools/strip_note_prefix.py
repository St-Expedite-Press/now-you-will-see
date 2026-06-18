"""Strip 'Note: ' prefix from Context Notes paragraphs in all reading-edition poems.

The 'Note: ' prefix is a drafting convention; clean prose paragraphs are the
target format. Paragraphs are separated by blank lines. This script rewrites
only the ## Context Notes section of each file.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
READING_ROOT = (
    REPO_ROOT
    / "projects/fletcher-complete-original-collections/manuscript/reading"
)

# Matches the Context Notes section through end-of-file or next ## heading
_NOTES_SECTION_RE = re.compile(
    r"(## Context Notes\n)(.*?)(?=\n## |\Z)", re.DOTALL
)
# Matches "Note: " at the start of a paragraph (start of section or after blank line)
_NOTE_PREFIX_RE = re.compile(r"(?m)^Note: ")


def _strip_prefixes(notes_body: str) -> str:
    return _NOTE_PREFIX_RE.sub("", notes_body)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "## Context Notes" not in text:
        return False

    def replacer(m: re.Match) -> str:
        heading = m.group(1)
        body = m.group(2)
        new_body = _strip_prefixes(body)
        return heading + new_body

    new_text = _NOTES_SECTION_RE.sub(replacer, text)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    updated = 0
    for md_file in sorted(READING_ROOT.rglob("*.md")):
        if md_file.name == "index.md":
            continue
        if process_file(md_file):
            updated += 1
    print(f"Updated: {updated}")


if __name__ == "__main__":
    main()
