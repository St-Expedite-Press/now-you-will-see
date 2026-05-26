"""Batch import service â€” ingest uploaded .md files into a section.

Detects frontmatter, assigns slugs, avoids collisions, and returns
a summary of what was imported.
"""

from __future__ import annotations

import sys
from pathlib import Path

from app.core.exceptions import ConflictError
from app.models.poem import PoemSummary

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def import_markdown_files(
    project_id: str,
    section_id: str,
    files: list[tuple[str, bytes]],  # (original_filename, content_bytes)
    overwrite: bool = False,
) -> list[PoemSummary]:
    """Import a batch of .md files into the named section.

    Returns a list of PoemSummary for successfully imported poems.
    """
    import frontmatter as fm
    from texgraph.utils import slugify

    from app.services import poem_service

    try:
        sec_dir = poem_service._section_dir(project_id, section_id)
    except Exception as exc:
        raise ConflictError(f"Section '{section_id}' not found")

    imported: list[PoemSummary] = []

    for original_name, raw_bytes in files:
        content_str = raw_bytes.decode("utf-8", errors="replace")
        try:
            post = fm.loads(content_str)
            title = post.metadata.get("title", Path(original_name).stem)
        except Exception:
            post = None
            title = Path(original_name).stem

        # Generate slug
        slug = slugify(str(title))
        dest = sec_dir / f"{slug}.md"

        if dest.exists() and not overwrite:
            raise ConflictError(f"File '{slug}.md' already exists in section '{section_id}'")

        dest.write_text(content_str, encoding="utf-8")

        line_count = len([l for l in (post.content if post else content_str).splitlines() if l.strip()])
        imported.append(PoemSummary(
            slug=slug,
            title=title,
            type=post.metadata.get("type", "poem") if post else "poem",
            order=post.metadata.get("order") if post else None,
            line_count=line_count,
        ))

    return imported

