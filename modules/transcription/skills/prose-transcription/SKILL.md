---
name: prose-transcription
description: "Transcribe prose source matter (prefaces, essays, dedications, colophons, publisher ads) from scanned pages into Markdown. Use for type: prose files, paragraph-based transcription, blockquote handling, and source paratext front matter."
module: transcription
tools:
  - texgraph new poem
  - texgraph audit
  - texgraph pdf text
---
# Prose Transcription

## Use When

Load this skill when the transcription task involves prose content:

- Prefaces, introductions, dedications, colophons, publisher advertisements
- Essays or critical prose within a volume
- Any matter that is paragraph-based, not line-by-line verse
- Filling `type: prose` front matter files created by the volume plan

Do not use for: verse transcription (`modules/transcription/skills/poem-transcription`),
volume planning (`modules/transcription/skills/volume-planning`), or metadata operations.

## Required Reads

Before editing files, read:

- `AGENTS.md`
- `modules/transcription/AGENTS.md`
- `README.md § Data Schemas` — source matter front matter spec
- The relevant volume plan
- The source scan pages for the piece being transcribed

## Workflow

1. Render the source pages before editing:
   ```powershell
   .\.venv\Scripts\texgraph.exe pdf render <pdf> --first N --last N --prefix <prefix>
   ```

2. Open the target file. If the file does not exist, create it with the correct
   front matter (see below) in the appropriate stage directory.

3. Set `type: prose` in front matter. Do not set `type: poem` on prose content.

4. Transcribe paragraph by paragraph. Each paragraph break in the source
   becomes a blank line in Markdown. Do not use `\\` or `<br>` for line ends
   within a paragraph.

5. For indented quotations or epigraphs in the source body, use `>` blockquote
   prefix on each line.

6. Preserve all punctuation as found. Do not normalize curly quotes to
   straight quotes, em-dashes to hyphens, or ellipses to periods.

7. Preserve non-ASCII characters (accented letters, ligatures) as Unicode.
   Do not use HTML entities.

8. For headings within the piece (chapter titles, section breaks), use
   `##` for section-level headings. Do not use `#` (reserved for document title).

9. Do not add formatting not present in the source (bold, italic) unless the
   source has visible emphasis.

10. If the source uses footnotes, transcribe the footnote marker inline as
    `[^n]` and add the footnote text at the bottom of the file as
    `[^n]: Footnote text.` Do not omit footnotes.

11. If a page is damaged or illegible, add a `notes` YAML entry:
    `notes: "p. 12: line 3 illegible"` and keep `status: transcribed`
    until resolved.

12. Set `status: transcribed` when complete and visually verified against scan.

## Source Matter Front Matter

```yaml
---
title: "Dedication"
book: "Book Title"
book_order: 1
matter_order: 1
matter_section: front         # front | back
matter_type: dedication       # see README.md for full list
source_pdf: "ingest/raw/<bucket>/<stable>.pdf"
source_pages_scan: "1-2"
source_pages_printed: "i-ii"
status: transcribed
notes: ""
---
```

Valid `matter_type` values:
`dedication`, `preface`, `contents`, `epigraph`, `acknowledgment`,
`illustration_list`, `frontispiece`, `dedicatory_poem`, `colophon`,
`publisher_ad`, `appendix`

## File Placement

Source paratext files belong in:
```
projects/<project_id>/transcription/<volume>/books/<book>/front_matter/
projects/<project_id>/transcription/<volume>/books/<book>/back_matter/
```

Prose sections destined for the typeset build belong in:
```
projects/<project_id>/interior/content/<section>/<file>.md
```

Confirm placement with the volume plan before creating files.

## Guardrails

- Do not invent missing text. Record uncertainty in `notes`.
- Do not use external texts to fill gaps unless the user permits; record in `notes`.
- Do not alter verse line breaks — if content is verse within a prose piece
  (quoted poetry), switch to `modules/transcription/skills/poem-transcription` for that excerpt.
- Cross-stage writes require user approval.
