#!/usr/bin/env python3
"""
scaffold_typeset_poems.py — Scaffold reading-edition poem files from transcription.

Reads documentary poem files from the project's transcription volumes and
scaffolds reading-edition files in the manuscript module
(`manuscript/reading/<section>/`), in the three-section format defined by the
project's manuscript/EDITORIAL_PROCEDURE.md:

    ## Original Lineation   <- written by this tool, verbatim witness body
    ## Editorial Relineation  (added later, by hand)
    ## Context Notes          (added later, by hand)

SAFETY: existing files are NEVER overwritten by default. The reading edition
is hand-curated manuscript data; a batch overwrite destroyed editorial notes
once (2026-06-01). Use --force only when you mean to discard hand work.

Usage:
    python machinery/tools/scaffold_typeset_poems.py
    python machinery/tools/scaffold_typeset_poems.py --dry-run
    python machinery/tools/scaffold_typeset_poems.py --force   # destructive
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

DEFAULT_PROJECT = "fletcher-early-works"


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
    while result and not result[0].strip():
        result.pop(0)
    text = "\n".join(result).rstrip("\n") + "\n"
    return text


def build_reading_fm(fm: dict) -> str:
    data: dict = {
        "title": fm.get("title", ""),
        "type": "poem",
        "order": fm.get("poem_order", 1),
    }
    part = fm.get("book_part")
    if part:
        data["part"] = part
    return yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)


def resolve_roots(project_root: Path) -> tuple[Path, Path]:
    """Resolve transcription source and reading-edition destination roots.

    Prefers canonical module directories; falls back to legacy names for
    unmigrated projects.
    """
    transcription = project_root / "transcription"
    if not transcription.exists():
        transcription = project_root / "transcribe"
    src = transcription / "volumes" / "01_early_works" / "books"

    if (project_root / "manuscript").exists() or not (project_root / "typeset").exists():
        dest = project_root / "manuscript" / "reading"
    else:
        dest = project_root / "typeset" / "content"
    return src, dest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT,
                        help="Project ID under projects/ (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written without writing files")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing files (DESTRUCTIVE: discards "
                             "hand-edited relineation and notes)")
    args = parser.parse_args()

    root = repo_root()
    project = root / "projects" / args.project
    src_root, dest_root = resolve_roots(project)

    written = 0
    skipped = 0
    for book_dir, section_dir in BOOK_MAP.items():
        poems_src = src_root / book_dir / "poems"
        if not poems_src.exists():
            print(f"  [skip] missing: {poems_src}")
            continue

        out_dir = dest_root / section_dir
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)

        for poem_file in sorted(poems_src.glob("*.md")):
            out_path = out_dir / poem_file.name
            if out_path.exists() and not args.force:
                skipped += 1
                continue

            text = poem_file.read_text(encoding="utf-8-sig")
            fm, body = parse_frontmatter(text)
            body = strip_heading(body)
            reading_fm = build_reading_fm(fm)
            out_text = (
                f"---\n{reading_fm}---\n\n"
                f"## Original Lineation\n\n{body}"
            )

            if args.dry_run:
                print(f"  would write: {out_path.relative_to(root)}")
            else:
                out_path.write_text(out_text, encoding="utf-8")
                print(f"  wrote: {out_path.relative_to(root)}")
            written += 1

    verb = "would write" if args.dry_run else "wrote"
    print(f"\n{verb} {written} poem file(s); skipped {skipped} existing "
          f"(use --force to overwrite hand-curated files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
