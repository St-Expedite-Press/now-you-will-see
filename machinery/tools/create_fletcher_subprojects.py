from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "projects" / "early-works-fletcher-1" / "typeset"
RAW = PARENT / "raw"
WORKSPACE = ROOT / "workspace.yaml"


RAW_FILES = [
    "fletcher-john-gould--visions-of-the-evening.md",
    "fletcher-john-gould--fire-and-wine.md",
    "fletcher-john-gould--dominant-city.md",
    "fletcher-john-gould--book-of-nature.md",
    "fletcher-john-gould--goblins-and-pagodas.md",
]

STANDALONE_PROJECT_SLUGS = {"goblins-and-pagodas"}


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"['`]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"


def q(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def parse_raw(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---", 4)
    if end == -1:
        return {}, text

    meta_text = text[4:end].strip()
    body = text[text.find("\n", end + 1) + 1 :]
    meta = yaml.safe_load(meta_text) or {}
    return dict(meta), body


def strip_title_block(body: str, title: str) -> str:
    lines = body.splitlines()
    start = 0

    # Drop the book title display block, which is duplicated in collection.yaml.
    for i, line in enumerate(lines[:20]):
        if line.strip() == "---":
            start = i + 1
            break

    if start:
        return "\n".join(lines[start:]).strip()

    title_norm = normalize_title(title)
    kept: list[str] = []
    dropping = True
    for line in lines:
        stripped = line.strip()
        if dropping and (
            normalize_title(stripped.lstrip("#").strip()) == title_norm
            or stripped.startswith("*")
            or not stripped
        ):
            continue
        dropping = False
        kept.append(line)
    return "\n".join(kept).strip()


def normalize_title(text: str) -> str:
    text = re.sub(r"^[#>\s]+", "", text)
    text = re.sub(r"[*_`]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .:;-").casefold()


def clean_heading(text: str) -> str:
    text = re.sub(r"[*_`]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def combine_title(parent: str, child: str) -> str:
    parent = clean_heading(parent).strip(" .")
    child = clean_heading(child).strip(" .")
    if not parent:
        return child
    if parent.casefold() in {"to", "part i", "part ii", "part iii", "part iv", "part v"}:
        return f"{parent} {child}"
    if parent.casefold().startswith("part "):
        return f"{parent}: {child}"
    if len(parent) <= 12 and child:
        return f"{parent}: {child}"
    return child


def is_bodyless(lines: list[str]) -> bool:
    return not any(line.strip() for line in lines)


def clean_body_line(line: str) -> str:
    line = line.replace("&nbsp;", "  ")
    line = line.replace("\ufeff", "")
    return line.rstrip()


def split_pieces(meta: dict[str, object], body: str) -> list[tuple[str, list[str]]]:
    book_title = str(meta.get("title") or "Untitled")
    book_norm = normalize_title(book_title)
    pieces: list[tuple[str, list[str]]] = []
    current_title = ""
    current_lines: list[str] = []
    seen_real_heading = False

    def finish() -> None:
        nonlocal current_title, current_lines
        lines = trim_blank(current_lines)
        if current_title and any(line.strip() for line in lines):
            pieces.append((current_title, lines))
        current_title = ""
        current_lines = []

    for raw_line in body.splitlines():
        line = clean_body_line(raw_line)
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            current_lines.append(line)
            continue

        level = len(match.group(1))
        heading = clean_heading(match.group(2))
        heading_norm = normalize_title(heading)

        if level == 1 and heading_norm == book_norm:
            continue

        if level <= 2:
            if heading_norm == book_norm and current_title and not is_bodyless(current_lines):
                # OCR/page running title inside a poem.
                continue
            if heading_norm == book_norm and seen_real_heading and is_bodyless(current_lines):
                # Repeated book title just before the real poem title.
                current_title = ""
                current_lines = []
                continue
            finish()
            current_title = heading
            current_lines = []
            if heading_norm != book_norm:
                seen_real_heading = True
            continue

        if not current_title:
            current_title = heading
            current_lines = []
            seen_real_heading = True
            continue

        if is_bodyless(current_lines):
            current_title = combine_title(current_title, heading)
            seen_real_heading = True
            continue

        current_lines.extend(["", f"**{heading}**", ""])

    finish()

    if pieces:
        return pieces

    fallback = trim_blank([clean_body_line(line) for line in body.splitlines()])
    return [(book_title, fallback)]


def trim_blank(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def write_project(raw_path: Path) -> tuple[str, int]:
    meta, body = parse_raw(raw_path)
    title = str(meta.get("title") or raw_path.stem)
    author = str(meta.get("author") or "John Gould Fletcher")
    year = int(meta.get("year") or 2025)
    publisher = str(meta.get("publisher") or "")

    project_slug = slugify(title)
    if project_slug in STANDALONE_PROJECT_SLUGS:
        project_id = project_slug
        project_dir = ROOT / "projects" / project_slug / "typeset"
        subtitle = "A standalone staged publishing project"
    else:
        project_id = f"early-works-fletcher-1-{project_slug}"
        project_dir = PARENT / project_slug
        subtitle = "A staged publishing subproject from Early Works"
    content_dir = project_dir / "content" / "01_text"
    output_dir = project_dir / "output"
    content_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    (project_dir / ".texgraph-generated-from-raw").write_text(
        f"{raw_path.relative_to(ROOT).as_posix()}\n", encoding="utf-8"
    )

    collection = "\n".join(
        [
            "# Collection Metadata",
            f"title: {q(title)}",
            f"subtitle: {q(subtitle)}",
            f"author: {q(author)}",
            'author_short: "Fletcher"',
            f"year: {year}",
            "language: en",
            f"publisher: {q(publisher)}",
            'publisher_location: ""',
            'isbn: ""',
            'rights: "Public-domain source text; editorial arrangement pending."',
            'content_dir: "content"',
            'output_dir: "output"',
            'lualatex_path: "lualatex"',
            "draft_mode: false",
            "pdfx:",
            '  output_intent: "PDFX-3:2002"',
            '  document_id: "00000000-0000-0000-0000-000000000000"',
            "sections:",
            "  - id: text",
            f"    label: {q(title)}",
            f"    note: {q(raw_path.name)}",
            "",
        ]
    )
    (project_dir / "collection.yaml").write_text(collection, encoding="utf-8")

    section_meta = "\n".join(
        [
            "id: text",
            "type: section",
            f"label: {q(title)}",
            "order: 1",
            f"source: {q(raw_path.name)}",
            "",
        ]
    )
    (content_dir / "_meta.yaml").write_text(section_meta, encoding="utf-8")

    clean_body = strip_title_block(body, title)
    pieces = split_pieces(meta, clean_body)
    used: dict[str, int] = {}
    for order, (piece_title, lines) in enumerate(pieces, start=1):
        base_slug = slugify(piece_title)
        count = used.get(base_slug, 0) + 1
        used[base_slug] = count
        poem_slug = base_slug if count == 1 else f"{base_slug}-{count}"
        poem_text = "\n".join(
            [
                "---",
                f"title: {q(piece_title)}",
                "type: poem",
                f"order: {order}",
                'dedication: ""',
                'epigraph: ""',
                'epigraph_author: ""',
                "---",
                "",
                "\n".join(lines).strip(),
                "",
            ]
        )
        (content_dir / f"{poem_slug}.md").write_text(poem_text, encoding="utf-8")

    return project_id, len(pieces)


def update_workspace(project_ids: list[str]) -> None:
    data = yaml.safe_load(WORKSPACE.read_text(encoding="utf-8")) or {}
    projects = data.setdefault("projects", [])
    existing = {entry.get("id") for entry in projects if isinstance(entry, dict)}

    for project_id in project_ids:
        if project_id in existing:
            continue
        slug = project_id.removeprefix("early-works-fletcher-1-")
        path = (
            f"projects/{slug}/typeset"
            if slug in STANDALONE_PROJECT_SLUGS
            else f"projects/early-works-fletcher-1/{slug}"
        )
        description = (
            f"Standalone Fletcher project: {slug.replace('-', ' ').title()}"
            if slug in STANDALONE_PROJECT_SLUGS
            else f"Fletcher early works subproject: {slug.replace('-', ' ').title()}"
        )
        projects.append(
            {
                "id": project_id,
                "path": path,
                "description": description,
            }
        )

    WORKSPACE.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def main() -> None:
    made: list[str] = []
    for name in RAW_FILES:
        project_id, piece_count = write_project(RAW / name)
        made.append(project_id)
        print(f"{project_id}: {piece_count} pieces")
    update_workspace(made)


if __name__ == "__main__":
    main()
