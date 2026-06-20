from __future__ import annotations

from pathlib import Path

from backend.core.env import repo_root
from backend.core.models import parse_front_matter

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
