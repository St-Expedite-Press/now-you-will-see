---
name: transcription-verification
description: Audit completed transcription work in the Fletcher scanned poetry repo. Use when checking poem/source-matter statuses, source-page spans, forbidden markup, poem counts, checklist completion, book.json consistency, temporary render cleanup, and readiness for checked or final status.
---

# Transcription Verification

## Checks

Run focused checks for:

- pending statuses that should be resolved
- `source_pages_scan: null`
- missing or incorrect printed page spans
- code fences, HTML entities, `<br>`, and visible page-break markers
- unchecked entries in the relevant `book.md`
- temporary rendered scan files in the workspace root
- poem count matching the volume checklist
- source front/back matter staying outside poem counts
- `book.json` matching `book.md` and folder counts

Use the deterministic audit helper first:

```powershell
fletcher audit volumes\<volume>\books\<book>
```

Then validate book metadata when structure or source matter changed:

```powershell
fletcher metadata volumes --check
```

## Status Rules

Use `transcribed` for first-pass image-checked transcription.
Use `checked` only after a separate recheck against page images.
Use `final` only when publication review is complete.

Source matter follows the same status values, but it does not affect poem
counts. Verify it through `book.json` counts and direct file review.

## Cleanup

Before deleting temporary renders, resolve paths under the current workspace and
delete only the intended temporary files.
