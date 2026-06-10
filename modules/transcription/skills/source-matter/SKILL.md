---
name: source-matter
description: Transcribe and manage source-book front and back matter. Use when handling dedications, prefaces, contents pages, acknowledgments, illustration lists, epigraphs, colophons, publisher ads, or other source paratext under a book's front_matter/ or back_matter/ folders.
---

# Source Matter

## Scope

Use this skill for source paratext from an original book scan:

- `projects/<project_id>/transcription/<volume>/books/<book>/front_matter/`
- `projects/<project_id>/transcription/<volume>/books/<book>/back_matter/`

Do not use it for edition-level introductions, afterwords, or textual notes;
those belong under `projects/<project_id>/transcription/<volume>/front_matter/` and
`projects/<project_id>/transcription/<volume>/back_matter/`.

For general prose transcription workflow, also read
`modules/transcription/skills/prose-transcription/SKILL.md`.

## Workflow

1. Read `AGENTS.md`, `transcribe/AGENTS.md`, the target `book.md`, and any
   project-level editorial policy under `projects/<project_id>/transcription/metadata/`.
2. Render/open the relevant source scan pages before editing:
   ```powershell
   .\.venv\Scripts\texgraph.exe pdf render <pdf> --first <n> --last <n> --prefix <prefix>
   ```
3. Use OCR only for navigation and checking.
4. Treat contents-listed poems as poems, even if titled "Invocation" or
   "Preface". Treat unnumbered dedications, prefaces, contents pages,
   acknowledgments, illustration lists, colophons, and publisher ads as source
   matter.
5. When a missing source-matter item is found in a book within an already active
   volume, check sibling books in that volume for the same class of omission
   before closing the task. Typical omissions: unnumbered dedicatory poems,
   printer statements, final colophons.
6. Store source matter in the book's `front_matter/` or `back_matter/` folder,
   not in `poems/`.
7. Use YAML plus one H1 heading. Required YAML fields:
   `title`, `book`, `book_order`, `matter_order`, `matter_section`,
   `matter_type`, `source_pdf`, `source_pages_scan`, `source_pages_printed`,
   `status`, `notes`
   See `ONTOLOGY.md § Data Schemas` for the full schema.
8. Use `matter_section: "front"` or `matter_section: "back"`.
9. Valid `matter_type` values: `dedication`, `preface`, `contents`, `epigraph`,
   `acknowledgment`, `illustration_list`, `frontispiece`, `dedicatory_poem`,
   `colophon`, `publisher_ad`, `appendix`.
10. Preserve documentary text, lineation, and meaningful spacing. Do not use
    code fences, HTML entities, `<br>`, or visible page-break markers.
11. Set `status: "transcribed"` only after visual image checking.
12. Regenerate book metadata after adding or removing source matter:
    ```powershell
    .\.venv\Scripts\texgraph.exe metadata projects/<project_id>/transcription/volumes --write --check
    ```

## Inventory

Refresh the source matter inventory after source acquisition or replacement:

```powershell
.\.venv\Scripts\texgraph.exe scan projects/<project_id>/transcription/volumes --output projects/<project_id>/transcription/metadata/source_matter_inventory.md
```

The inventory is a navigation aid. Visually review image-only sources and
ambiguous OCR hits before creating or updating source matter files.
