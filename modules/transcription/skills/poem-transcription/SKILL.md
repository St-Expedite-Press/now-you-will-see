---
name: poem-transcription
description: Transcribe poems from scanned page images into clean Markdown. Use when filling one poem per Markdown file, preserving lineation and indentation, normalizing drop caps, handling multipage poems, distinguishing poems from source paratext, and updating poem YAML metadata.
---

# Poem Transcription

## Required Reads

Before editing poem files, read:

- `AGENTS.md`
- `transcribe/AGENTS.md`
- `modules/transcription/skills/poem-transcription/SKILL.md`
- `projects/fletcher-complete-original-collections/transcribe/metadata/editorial_policy.md`
- the relevant volume plan in `projects/fletcher-complete-original-collections/transcribe/metadata/`
- the relevant `books/<volume>/book.md`

## Workflow

1. When asked to transcribe a volume, fill the poem Markdown files. Do not stop
   at a plan unless the user explicitly asks only for a plan.
2. Render or open the relevant scan page before editing:
   ```powershell
   .\.venv\Scripts\texgraph.exe pdf render <pdf> --first <n> --last <n> --prefix <prefix>
   ```
3. Use OCR only to navigate or check readings:
   ```powershell
   .\.venv\Scripts\texgraph.exe pdf text <pdf> --first <n> --last <n> --output <file>
   ```
   Do not paste unchecked OCR as the final text.
4. Transcribe into the existing poem file.
5. Use YAML front matter with the repository's standard fields.
6. Use one `# Title` heading.
7. Preserve original line breaks, stanza breaks, and meaningful leading spaces.
   Preserve visible source hyphenation at line breaks during transcription;
   modernization or silent joining belongs in a later editorial pass.
8. Do not use code fences, HTML entities, `<br>`, or visible page-break markers.
9. Normalize drop caps silently into ordinary text.
10. Keep multipage poems in one file and record all scan and printed pages.
11. For cycles, follow the volume plan or contents-page evidence. If the source
    presents roman-numbered internal sections under one contents item, keep one
    poem file and use `## I.`, `## II.`, etc. section headings.
12. For unnumbered invocation, dedication, dedicatory poem, prefatory, or
    reader-address material, do not force the item into the numbered poem
    sequence unless the contents page lists it as a poem. Put it in
    `projects/fletcher-complete-original-collections/transcribe/volumes/<volume>/books/<book>/front_matter/` with YAML fields for
    `title`, `book`, `book_order`, `matter_order`, `matter_section`,
    `matter_type`, `source_pdf`, `source_pages_scan`, `source_pages_printed`,
    `status`, and `notes`. For substantial source paratext work, switch to
    `modules/transcription/skills/source-matter/SKILL.md`.
13. If the source page title differs from the scaffold, let the source govern:
    update YAML title, H1, checklist text, and filename when practical.
14. If a scan contradicts the scaffold or volume plan, correct the current poem
    and adjacent affected spans immediately; update the volume plan as part of
    the same batch.
15. Set `status: "transcribed"` only after visual image checking.
16. Update the volume checklist and book-level `transcription_status` when the
    whole volume is complete.

## Uncertain Text

Do not invent unreadable readings. If a page is damaged or blurred, add a YAML
`notes` entry and keep the status honest. Use external texts only when the user
permits or the source page is unusable, and record that in `notes`.

