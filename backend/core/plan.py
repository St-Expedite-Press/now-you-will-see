from __future__ import annotations

import re
from pathlib import Path


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_STALE_CITE_RE = re.compile(r"(?:cite[^\n]{0,40}turn\d+)|turn\d+(?:view|search|news|reddit)\d+")


def _slug(title: str) -> str:
    text = title.strip().lower()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[*_]", "", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def headings(path: Path) -> list[tuple[int, str, str]]:
    rows: list[tuple[int, str, str]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m = _HEADING_RE.match(line)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2).strip()
        rows.append((level, title, _slug(title)))
    return rows


def _print_index(path: Path) -> int:
    for level, title, anchor in headings(path):
        indent = "  " * (level - 1)
        print(f"{indent}- [{title}](#{anchor})")
    return 0


def _check(path: Path) -> int:
    text = path.read_text(encoding="utf-8-sig")
    issues: list[str] = []
    rows = headings(path)
    if not rows:
        issues.append("no markdown headings found")
    if "# Index" not in text:
        issues.append("missing '# Index' section")
    if "# Appendix" not in text and "## Appendix" not in text:
        issues.append("missing appendix headings")
    stale = _STALE_CITE_RE.findall(text)
    if stale:
        issues.append(f"stale citation tokens found: {len(stale)}")
    anchors = [a for _, _, a in rows]
    for dup in sorted({a for a in anchors if anchors.count(a) > 1}):
        issues.append(f"duplicate heading anchor: {dup}")
    if issues:
        for issue in issues:
            print(f"ISSUE: {issue}")
        return 1
    print(f"ok headings={len(rows)}")
    return 0
