from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from fletcher.env import repo_root, resolve_in_repo
from fletcher.models import BookFrontMatter, VolumeFrontMatter, first_heading, parse_front_matter

_SERIES_DEFAULT = "John Gould Fletcher: The Complete Original Collections"


def _rights_status(raw: dict[str, Any]) -> str:
    if raw.get("rights_status"):
        return str(raw["rights_status"])
    year = raw.get("year")
    if isinstance(year, int) and year < 1931:
        return "public_domain"
    return "unknown"


def _count_md(directory: Path) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob("*.md")))


def _volume_metadata(volume_dir: Path) -> dict[str, Any]:
    volume_md = volume_dir / "volume.md"
    text = volume_md.read_text(encoding="utf-8-sig")
    vol = VolumeFrontMatter.model_validate(parse_front_matter(text))
    return {
        "volume_id": volume_dir.name,
        "volume_order": vol.volume_order,
        "volume_title": vol.title or first_heading(text),
        "series": vol.series or _SERIES_DEFAULT,
    }


def build_metadata(book_dir: Path) -> dict[str, Any]:
    root = repo_root()
    book_md = book_dir / "book.md"
    if not book_md.exists():
        raise SystemExit(f"missing book.md: {book_dir.relative_to(root)}")
    volume_dir = book_dir.parents[1]
    volume = _volume_metadata(volume_dir)
    text = book_md.read_text(encoding="utf-8-sig")
    raw = parse_front_matter(text)
    bk = BookFrontMatter.model_validate(raw)
    return {
        "id": book_dir.name,
        "series": volume["series"],
        "volume_id": volume["volume_id"],
        "volume_order": volume["volume_order"],
        "volume_title": volume["volume_title"],
        "book_order": bk.book_order,
        "title": bk.title or first_heading(text),
        "author": bk.author,
        "publisher": bk.publisher,
        "place": bk.place,
        "year": bk.year,
        "source_pdf": bk.source_pdf,
        "source_status": bk.source_status,
        "pdf_pages": bk.pdf_pages,
        "rights_status": _rights_status(raw),
        "transcription_status": bk.transcription_status,
        "poem_count": _count_md(book_dir / "poems"),
        "front_matter_count": _count_md(book_dir / "front_matter"),
        "back_matter_count": _count_md(book_dir / "back_matter"),
        "notes": bk.notes,
    }


def book_dirs(target: Path) -> list[Path]:
    if target.name.startswith("books") and target.is_dir():
        return sorted(p for p in target.iterdir() if (p / "book.md").exists())
    if (target / "book.md").exists():
        return [target]
    return sorted(p.parent for p in target.glob("**/book.md"))


def _write_json(book_dir: Path, metadata: dict[str, Any]) -> None:
    out = book_dir / "book.json"
    out.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _check_json(book_dir: Path, metadata: dict[str, Any]) -> list[str]:
    path = book_dir / "book.json"
    if not path.exists():
        return [f"{book_dir.relative_to(repo_root())}: missing book.json"]
    if json.loads(path.read_text(encoding="utf-8-sig")) != metadata:
        return [f"{book_dir.relative_to(repo_root())}: book.json is stale or inconsistent"]
    return []


def _run(args: argparse.Namespace) -> int:
    target = resolve_in_repo(args.target)
    books = book_dirs(target)
    if not books:
        raise SystemExit(f"no book.md files found under: {target.relative_to(repo_root())}")

    all_metadata = [build_metadata(b) for b in books]
    if args.write:
        for book, meta in zip(books, all_metadata, strict=True):
            _write_json(book, meta)

    issues: list[str] = []
    if args.check:
        for book, meta in zip(books, all_metadata, strict=True):
            issues.extend(_check_json(book, meta))

    if args.json:
        print(json.dumps(all_metadata, indent=2, ensure_ascii=False))
    else:
        print(f"books={len(books)}")
        if args.write:
            print("wrote=book.json")
        if args.check:
            print(f"issues={len(issues)}")
            for issue in issues:
                print(f"  {issue}")

    return 1 if issues else 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("metadata", help="Generate or validate per-book book.json metadata.")
    p.add_argument("target", help="Book, books, volume, or volumes directory.")
    p.add_argument("--write", action="store_true", help="Write book.json files.")
    p.add_argument("--check", action="store_true", help="Check book.json files for staleness.")
    p.add_argument("--json", action="store_true", help="Print generated metadata as JSON.")
    p.set_defaults(func=_run)
