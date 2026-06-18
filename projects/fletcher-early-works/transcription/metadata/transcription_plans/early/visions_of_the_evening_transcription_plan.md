# Visions of the Evening Transcription Plan

## Summary

Transcribe _Visions of the Evening_ from
`raw/early_1913/visions_of_the_evening.pdf` into
`volumes/01_early_works/books/05_visions_of_the_evening/poems/`, preserving the same documentary
format used for the preceding volumes: one Markdown file per poem, YAML
metadata, H1 title, image-checked transcription, no visible page-break markers.

Use neutral transcription mode only. Do not use SandbatchAgent for poem bodies,
YAML, page spans, checklist work, command summaries, or cleanup.

## Source State

- Source PDF: `raw/early_1913/visions_of_the_evening.pdf`
- Manifest page count: 56 PDF pages
- Volume scaffold: 40 poem files, all pending
- Body source map visually confirmed from scans:
  - printed page 1 = scan page 9
  - printed page 3 = scan page 11
  - printed page 43 = scan page 51
- Body-page formula: `scan = printed + 8`
- Body span: printed pages 1-43 = scans 9-51
- Front matter:
  - scans 7-8 contain the contents list
  - scans before 9 are not poem body pages
- Back matter:
  - scan 52 contains the Arden Press colophon

## Preflight

Before transcription begins:

1. Read `AGENTS.md`, `metadata/editorial_policy.md`,
   `metadata/source_manifest.md`,
   `volumes/01_early_works/books/05_visions_of_the_evening/book.md`, and relevant `machinery/skills/`.
2. Confirm the source PDF exists:

   ```powershell
   Test-Path raw\early_1913\visions_of_the_evening.pdf
   ```

3. Audit the scaffold:

   ```powershell
   .\.venv\Scripts\python.exe machinery\tools\audit_transcription.py books\05_visions_of_the_evening --json
   ```

4. Expected pre-transcription audit state:
   - 40 poem files
   - 40 `pending` statuses
   - all checklist entries unchecked
   - `source_pages_scan: null` in all poem files

## Expected Poem Spans

The table below derives scan spans from the visually confirmed offset
`scan = printed + 8`. Contents-derived start pages remain provisional until the
body pages are checked during transcription.

| Order | Poem | Printed Pages | Scan Pages |
|---:|---|---:|---:|
| 1 | To the Immortal Memory of Charles Baudelaire | 1-2 | 9-10 |
| 2 | Invocation to Evening | 3-4 | 11-12 |
| 3 | Invocation to Solitude | 5 | 13 |
| 4 | Invocation to Night | 6 | 14 |
| 5 | The Lover of Solitude | 7 | 15 |
| 6 | The Valley of Kashmir | 8 | 16 |
| 7 | The Irony of Night | 9 | 17 |
| 8 | Towards the Impossible | 10 | 18 |
| 9 | I Contemplate My Toil | 11 | 19 |
| 10 | Vision after Midnight | 12 | 20 |
| 11 | Futility | 13 | 21 |
| 12 | My Hours | 14 | 22 |
| 13 | Anatomy of Myself | 15 | 23 |
| 14 | The Albatross | 16 | 24 |
| 15 | The Caged Eagle | 17 | 25 |
| 16 | Misfortune | 18 | 26 |
| 17 | Golgotha | 19 | 27 |
| 18 | The Descent into Hell | 20 | 28 |
| 19 | Midnight Prayer | 21 | 29 |
| 20 | Remembrances | 22 | 30 |
| 21 | The Lid | 23 | 31 |
| 22 | On a Windy Day | 24 | 32 |
| 23 | Woman | 25 | 33 |
| 24 | From the Japanese | 26 | 34 |
| 25 | From the Chinese | 27 | 35 |
| 26 | The Mystic Vision | 28 | 36 |
| 27 | Adrift | 29 | 37 |
| 28 | Clouds | 30-31 | 38-39 |
| 29 | The Body to the Soul | 32 | 40 |
| 30 | Dead Thoughts | 33 | 41 |
| 31 | Day and Night | 34 | 42 |
| 32 | Greatness and Littleness | 35 | 43 |
| 33 | The Everlasting Paradox | 36 | 44 |
| 34 | Dreams | 37 | 45 |
| 35 | The Songs of Silence | 38 | 46 |
| 36 | Summer Sleep | 39 | 47 |
| 37 | End of the Revel | 40 | 48 |
| 38 | The Smoke of Dreams | 41 | 49 |
| 39 | My Grave | 42 | 50 |
| 40 | My Monument | 43 | 51 |

## Transcription Batches

- Batch 1: scans 9-16, printed pages 1-8:
  `To the Immortal Memory of Charles Baudelaire` through
  `The Valley of Kashmir`.
- Batch 2: scans 17-24, printed pages 9-16:
  `The Irony of Night` through `The Albatross`.
- Batch 3: scans 25-32, printed pages 17-24:
  `The Caged Eagle` through `On a Windy Day`.
- Batch 4: scans 33-40, printed pages 25-32:
  `Woman` through `The Body to the Soul`.
- Batch 5: scans 41-51, printed pages 33-43:
  `Dead Thoughts` through `My Monument`.

Render each batch through the repo-local venv, for example:

```powershell
.\.venv\Scripts\python.exe machinery\tools\pdf_pages.py render raw\early_1913\visions_of_the_evening.pdf --first 9 --last 16 --prefix tmp_ve_batch1 --dpi 220
```

## Per-Poem Rules

- Open and inspect every rendered scan page before editing the poem file.
- Use OCR only as a navigation or checking aid.
- Normalize drop caps into ordinary first words.
- Preserve visible line breaks, stanza breaks, and meaningful continuation
  indentation with ordinary spaces.
- Keep subtitles or parenthetical source subtitles in the poem body below the
  H1 when they appear as source text.
- Do not insert page-break markers into poem bodies.
- Set `source_pages_scan`, `source_pages_printed`, and `status: "transcribed"`
  only after image checking the complete poem span.
- If the source title differs from the scaffold title, update YAML title, H1,
  checklist entry, and filename to match the source.

## Known Span Notes

- `To the Immortal Memory of Charles Baudelaire` is expected to span printed
  pages 1-2, scans 9-10.
- `Invocation to Evening` is expected to span printed pages 3-4, scans 11-12.
- `Clouds` is expected to span printed pages 30-31, scans 38-39.
- All other contents entries are expected to be single printed-page poems, but
  body images remain authoritative.

## Completion

When transcription is complete:

1. Update every checklist item in
   `volumes/01_early_works/books/05_visions_of_the_evening/book.md`.
2. Set book-level `transcription_status: "transcribed"`.
3. Remove temporary `tmp_ve*.png` render files after verifying their resolved
   paths are inside the repo root.

## Test Plan

Run:

```powershell
.\.venv\Scripts\python.exe machinery\tools\audit_transcription.py books\05_visions_of_the_evening
rg 'status: "pending"|source_pages_scan: null|```|<br|&quot;|page-break|PAGE BREAK' books\05_visions_of_the_evening
Get-ChildItem -Name tmp_ve*.png
```

Acceptance criteria:

- 40 poem files.
- All statuses are `transcribed`.
- No missing scan-page spans.
- No unchecked checklist entries.
- No forbidden markup or visible page-break annotations.
- No temporary render files remain.
- `book.md` says `transcription_status: "transcribed"`.

## Assumptions

- The visually confirmed body-page mapping `scan = printed + 8` remains stable
  across printed pages 1-43.
- The existing contents scaffold is authoritative unless the scan page clearly
  contradicts it.
- First-pass completion means `transcribed`, not `checked`; `checked` requires
  a later separate verification pass against page images.

