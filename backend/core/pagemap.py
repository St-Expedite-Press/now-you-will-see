from __future__ import annotations

import re

# A LaTeX .toc entry: \contentsline {level}{title}{page}{...}
_TOC_LINE_RE = re.compile(
    r"\\contentsline\s*\{([^}]*)\}\{(.*)\}\{(\d+)\}", re.DOTALL
)


def parse_toc_pages(toc_text: str) -> list[tuple[str, str, int]]:
    """Parse a LaTeX ``.toc`` file into ``(level, title, page)`` tuples.

    Used to find the structurally important pages of a proof — book title
    pages, part dividers, the introduction, and the per-volume notes sections
    — so a reviewer can render exactly those leaves instead of guessing page
    numbers.  Titles keep their raw TeX; only the trailing page number is
    interpreted.
    """
    results: list[tuple[str, str, int]] = []
    for raw_level, raw_title, page in _TOC_LINE_RE.findall(toc_text):
        title = re.sub(r"\\numberline\s*\{[^}]*\}", "", raw_title).strip()
        results.append((raw_level.strip(), title, int(page)))
    return results


def expand_pages(spec: str) -> list[int]:
    """Expand a page range spec like '7-10,14,18' into a flat list of integers."""
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
            if end < start:
                raise SystemExit(f"Invalid page range: {part}")
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return pages
