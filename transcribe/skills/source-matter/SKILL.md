---
name: source-matter
description: Transcribe and manage source-book front and back matter in the Fletcher publication repo. Use when handling dedications, prefaces, contents pages, acknowledgments, illustration lists, epigraphs, colophons, publisher ads, or other source paratext under a book's front_matter/ or back_matter/ folders.
---

# Source Matter

## Scope

Use this skill for source paratext from an original book scan:

- `projects/fletcher-complete-original-collections/transcribe/volumes/<volume>/books/<book>/front_matter/`
- `projects/fletcher-complete-original-collections/transcribe/volumes/<volume>/books/<book>/back_matter/`

Do not use it for edition-level introductions, afterwords, or textual notes;
those belong under `projects/fletcher-complete-original-collections/transcribe/volumes/<volume>/front_matter/` and
`projects/fletcher-complete-original-collections/transcribe/volumes/<volume>/back_matter/`.

## Workflow

1. Read `AGENTS.md`, `projects/fletcher-complete-original-collections/transcribe/metadata/editorial_policy.md`, the target `book.md`, and
   `projects/fletcher-complete-original-collections/transcribe/metadata/source_matter_inventory.md`.
2. Render/open the relevant source scan pages before editing. Use:
   `fletcher pdf render ...`.
3. Use OCR only for navigation and checking.
4. Treat contents-listed poems as poems, even if titled "Invocation" or
   "Preface". Treat unnumbered dedications, prefaces, contents pages,
   acknowledgments, illustration lists, colophons, and publisher ads as source
   matter.
5. When one missing source-matter item is found in a book within an already
   active volume, check the sibling books in that volume for the same class of
   omission before closing the task. Typical omissions are unnumbered
   dedicatory poems, printer statements, and final colophons.
6. Store source matter in the book's `front_matter/` or `back_matter/` folder,
   not in `poems/`.
7. Use YAML plus one H1 heading. Required YAML:
   `title`, `book`, `book_order`, `matter_order`, `matter_section`,
   `matter_type`, `source_pdf`, `source_pages_scan`, `source_pages_printed`,
   `status`, and `notes`.
8. Use `matter_section: "front"` or `matter_section: "back"`.
9. Use `matter_type` values such as `dedication`, `preface`, `contents`,
   `epigraph`, `acknowledgment`, `illustration_list`, `frontispiece`,
   `dedicatory_poem`, `colophon`, `publisher_ad`, or `appendix`.
10. Preserve documentary text, lineation, and meaningful spacing. Do not use
   code fences, HTML entities, `<br>`, or visible page-break markers.
11. Set `status: "transcribed"` only after visual image checking.
12. Regenerate book metadata after adding or removing source matter:
    `fletcher metadata volumes --write --check`.

## Inventory

Refresh the inventory after source acquisition or replacement:

```powershell
fletcher scan volumes --output metadata\source_matter_inventory.md
```

The inventory is a navigation aid. Visually review image-only sources and
ambiguous OCR hits before creating or updating source matter files.

