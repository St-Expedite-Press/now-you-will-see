"""Shared utility functions used by both the CLI and the Studio backend."""

from __future__ import annotations

import re
import unicodedata


def slugify(text: str) -> str:
    """Convert *text* to a filesystem-safe lowercase hyphenated slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "untitled"


def poem_scaffold(title: str, poem_type: str = "poem") -> str:
    """Return the content of a freshly scaffolded poem file."""
    return (
        "---\n"
        f'title: "{title}"\n'
        f"type: {poem_type}\n"
        "order:\n"
        "epigraph:\n"
        "dedication:\n"
        "---\n"
        "\n"
        "First line of the first stanza.\n"
        "Second line of the first stanza.\n"
        "\n"
        "First line of the second stanza.\n"
        "Second line of the second stanza.\n"
    )
