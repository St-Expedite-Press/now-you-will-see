---
name: volume-planning
description: Build or update a volume or book transcription plan for scanned Fletcher poetry books. Use when deriving contents, poem order, page offsets, batch ranges, source-page mappings, source front/back matter handling, or volume-specific transcription instructions.
---

# Volume Planning

## Workflow

1. Read `AGENTS.md`, `projects/fletcher-complete-original-collections/transcribe/metadata/editorial_policy.md`,
   `projects/fletcher-complete-original-collections/transcribe/metadata/source_manifest.md`, and the target
   `projects/fletcher-complete-original-collections/transcribe/volumes/<volume>/books/<book>/book.md`.
2. For structural or voice-led plans, read `PERSONA.md`; for neutral
   transcription plans, mention the persona boundary without using the register.
3. Confirm the source PDF is present and recorded.
4. Use contents pages, title pages, running headers, and first poem pages to
   build the poem checklist.
5. Identify source front and back matter separately from poem contents. Record
   unnumbered dedications, prefaces, contents pages, acknowledgments,
   illustration lists, colophons, and publisher ads in the book plan without
   adding them to poem counts.
6. Determine the scan-to-printed-page mapping from rendered images, not from OCR
   alone.
7. Use `fletcher page-map` for repetitive page-map
   calculations after the offset is visually confirmed.
8. Split the volume into small page batches that can be transcribed visually.
9. Treat contents-derived starts as provisional until the body scans are
   checked; if a previous poem continues onto an expected start page, update the
   plan and affected spans from the page images.
10. Record multipage poems and possible series/cycle handling before transcription.
11. Save the plan in `projects/fletcher-complete-original-collections/transcribe/metadata/transcription_plans/<era>/<volume>_transcription_plan.md`
    (e.g., `projects/fletcher-complete-original-collections/transcribe/metadata/transcription_plans/early/` for Volume 1 books).

## Plan Contents

Include scope, source map, page-by-page method, batch tables, and verification
criteria. If the mapping is tentative, say so and require visual confirmation.
Add a persona boundary when the volume will later need introduction, afterword,
or institutional framing.

Also include a front/back matter section when the source has dedications,
prefaces, contents pages, illustration lists, acknowledgments, colophons, or
publisher matter. Say whether each item will be transcribed, described in
apparatus, or deferred.

