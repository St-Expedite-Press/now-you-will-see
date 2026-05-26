from __future__ import annotations

import argparse
import json
from pathlib import Path

from fletcher.env import repo_root, resolve_in_repo
from fletcher.models import parse_front_matter

FORBIDDEN = ["```", "&nbsp;", "<br", "page-break", "PAGE BREAK"]


def forbidden_tokens(text: str) -> list[str]:
    """Return any forbidden markup tokens found in the given text."""
    return [token for token in FORBIDDEN if token in text]


def audit_book(book_dir: Path) -> dict[str, object]:
    poems = sorted((book_dir / "poems").glob("*.md"))
    issues: list[str] = []
    statuses: dict[str, int] = {}
    forbidden_hits: list[str] = []

    for poem in poems:
        text = poem.read_text(encoding="utf-8-sig")
        fields = parse_front_matter(text)
        status = str(fields.get("status", "missing"))
        statuses[status] = statuses.get(status, 0) + 1
        if fields.get("source_pages_scan") is None:
            issues.append(f"{poem.name}: source_pages_scan is missing or null")
        if fields.get("source_pages_printed") is None:
            issues.append(f"{poem.name}: source_pages_printed is missing or null")
        for token in forbidden_tokens(text):
            forbidden_hits.append(f"{poem.name}: {token!r}")

    book_md = book_dir / "book.md"
    unchecked: list[str] = []
    if book_md.exists():
        for idx, line in enumerate(book_md.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if line.startswith("- [ ]"):
                unchecked.append(f"book.md:{idx}: {line}")
    else:
        issues.append(f"{book_md.name}: missing")

    root = repo_root()
    tmp = sorted({p.name for p in root.glob("tmp_*.png")})

    return {
        "volume": str(book_dir.relative_to(root)),
        "poem_count": len(poems),
        "statuses": statuses,
        "issues": issues,
        "forbidden_hits": forbidden_hits,
        "unchecked": unchecked,
        "temporary_renders": tmp,
    }


def _run(args: argparse.Namespace) -> int:
    book_dir = resolve_in_repo(args.volume)
    result = audit_book(book_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"volume={result['volume']}")
        print(f"poem_count={result['poem_count']}")
        print(f"statuses={result['statuses']}")
        for key in ["issues", "forbidden_hits", "unchecked", "temporary_renders"]:
            values = result[key]
            print(f"{key}={len(values)}")  # type: ignore[arg-type]
            for v in values:  # type: ignore[union-attr]
                print(f"  {v}")
    bad = (
        result["issues"]
        or result["forbidden_hits"]
        or result["unchecked"]
        or result["temporary_renders"]
    )
    return 1 if bad else 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("audit", help="Audit a Fletcher transcription book directory.")
    p.add_argument(
        "volume",
        help="Example: volumes/01_early_works/books/02_the_dominant_city_1911_1912",
    )
    p.add_argument("--json", action="store_true", help="Output results as JSON.")
    p.set_defaults(func=_run)
