#!/usr/bin/env python3
"""
scaffold_typeset_poems.py — Convert transcription poems to typeset format.

Reads poem files from transcribe/volumes/01_early_works/books/*/poems/
and writes typeset-ready files to typeset/content/<section>/.

Strips transcription-specific YAML front matter and the # Title heading from
each poem body; outputs title/type/order/part front matter for the typeset stage.

Usage:
    python machinery/tools/scaffold_typeset_poems.py
    python machinery/tools/scaffold_typeset_poems.py --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


BOOK_MAP = {
    "01_the_book_of_nature_1910_1912": "01_the-book-of-nature",
    "02_the_dominant_city_1911_1912": "02_the-dominant-city",
    "03_fire_and_wine": "03_fire-and-wine",
    "04_fools_gold": "04_fools-gold",
    "05_visions_of_the_evening": "05_visions-of-the-evening",
}


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Cannot locate repo root.")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text
    fm = yaml.safe_load(match.group(1)) or {}
    body = text[match.end():]
    return fm, body


def strip_heading(body: str) -> str:
    """Remove the leading # Title line and any blank lines before poem text."""
    lines = body.split("\n")
    result: list[str] = []
    skipped = False
    for line in lines:
        if not skipped and line.strip().startswith("#"):
            skipped = True
            continue
        result.append(line)
    # Strip leading blank lines
    while result and not result[0].strip():
        result.pop(0)
    # Ensure single trailing newline
    text = "\n".join(result).rstrip("\n") + "\n"
    return text


def build_typeset_fm(fm: dict) -> str:
    data: dict = {
        "title": fm.get("title", ""),
        "type": "poem",
        "order": fm.get("poem_order", 1),
    }
    part = fm.get("book_part")
    if part:
        data["part"] = part
    return yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written without writing files")
    args = parser.parse_args()

    root = repo_root()
    project = root / "projects" / "fletcher-complete-original-collections"
    transcribe = project / "transcribe" / "volumes" / "01_early_works" / "books"
    typeset = project / "typeset" / "content"

    total = 0
    for book_dir, section_dir in BOOK_MAP.items():
        poems_src = transcribe / book_dir / "poems"
        if not poems_src.exists():
            print(f"  [skip] missing: {poems_src}")
            continue

        out_dir = typeset / section_dir
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)

        for poem_file in sorted(poems_src.glob("*.md")):
            text = poem_file.read_text(encoding="utf-8-sig")
            fm, body = parse_frontmatter(text)
            body = strip_heading(body)
            typeset_fm = build_typeset_fm(fm)
            out_text = f"---\n{typeset_fm}---\n\n{body}"
            out_path = out_dir / poem_file.name

            if args.dry_run:
                print(f"  would write: {out_path.relative_to(root)}")
            else:
                out_path.write_text(out_text, encoding="utf-8")
                print(f"  wrote: {out_path.relative_to(root)}")
            total += 1

    print(f"\n{'would write' if args.dry_run else 'wrote'} {total} poem files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
