# Editorial Policy

## Transcription

- Transcribe from page images, one scan page at a time.
- Use OCR only for navigation, contents checking, and post-transcription review.
- Preserve original lineation and stanza breaks.
- Preserve meaningful visible indentation with ordinary leading spaces in the
  Markdown source.
- Do not use code fences, HTML entities, or visible page-break markers in poem
  bodies.

## Drop Caps

Drop caps are not retained. Restore the affected first word or first line as
ordinary text.

## Multipage Poems

Continue the poem in the same Markdown file. Record the scan-page span and
printed-page span in YAML front matter.

## Series and Cycles

Series are handled case by case:

- If the source clearly presents a cycle as one titled work with internal
  numbered sections, keep the cycle in one file with internal `##` headings.
- If the contents page lists entries as separate poems, use separate files and
  connect them with `series`, `series_part`, and `book_part` metadata.

## Source Front And Back Matter

Source invocations, dedications, prefaces, epigraphs, contents pages,
acknowledgments, illustration lists, colophons, appendices, advertisements, and
other paratext belong in the source book's `front_matter/` or `back_matter/`
folder unless the source contents list the item as a poem. Use clean Markdown
with YAML metadata, an H1 title, scan page spans, `matter_section`, and
`matter_type` values such as `dedication`, `preface`, `contents`, `colophon`,
`dedicatory_poem`, or `publisher_ad`. Contents-listed invocations are treated
as poems.

When source-matter omissions are discovered in one book in an active volume,
review the sibling source books in that volume for comparable omissions before
closing the correction. The recurring early-volume cases are unnumbered
dedicatory poems, front-matter printer statements, and final colophons.

Volume-level editorial matter belongs under `volumes/<volume>/front_matter/`
and `volumes/<volume>/back_matter/`. These files are edition apparatus, not
source transcription, and should not be confused with source book paratext.

## Status Values

- `pending`: file scaffolded but not transcribed.
- `transcribed`: poem body entered from page images.
- `checked`: poem rechecked against page images.
- `final`: ready for publication.
