# The Dominant City Transcription Plan

## Scope

Transcribe _The Dominant City (1911-1912)_ after _The Book of Nature_.
The source is `raw/early_1913/the_dominant_city_1911_1912.pdf`, 88 PDF pages. The existing
target folder is `volumes/01_early_works/books/02_the_dominant_city_1911_1912/`, with 44 poem files
already scaffolded.

This is a transcription plan first and an editorial architecture plan second.
The poem files stay neutral, documentary, and source-bound. Any later
introduction, afterword, jacket copy, or institutional framing may invoke
SandbatchAgent.

## Agent Stack

Before work begins, read:

- `AGENTS.md`
- `machinery/skills/source-intake/SKILL.md`
- `machinery/skills/volume-planning/SKILL.md`
- `machinery/skills/poem-transcription/SKILL.md`
- `machinery/skills/transcription-verification/SKILL.md`
- `machinery/skills/sandbatch-editorial/SKILL.md`
- `metadata/editorial_policy.md`
- `volumes/01_early_works/books/02_the_dominant_city_1911_1912/book.md`

`AGENTS.md` routes work to repo-local skills, and
`machinery/skills/skill-improvement-loop/SKILL.md` must be used before the final response.

Read `SANDBATCH.md` only for structural, editorial, or voice-led work around
the volume. Do not let the Sandbatch register enter poem bodies, YAML metadata,
source manifests, or verification output.

## Register Boundary

- **Transcription register:** neutral, literal, image-checked, one poem per file.
- **Planning register:** direct and operational; use SandbatchAgent only when
  the user asks for voice-led structure or editorial architecture.
- **Editorial register:** SandbatchAgent is available for the later volume
  introduction and afterword, especially for placing Fletcher's city poems
  inside early modernist compression, Southern modernist displacement, and the
  apparatus of dimensional reduction.
- **Metadata register:** never Sandbatch; keep it parseable and boring.

## Source Map

The first poem starts on printed page 7 and scan page 13. Use the working
offset `scan page = printed page + 6` for the poem body, subject to visual
confirmation from the rendered page image.

The poem text runs from printed page 7 through printed page 75:

- poem body scan range: 13-81
- printed page range: 7-75
- front matter and contents: scans 1-12
- printer/back matter begins after scan 81

## Execution Method

1. Render the next small batch of scan pages with `pdftoppm`.
2. Open one rendered page image at a time.
3. Use `pdftotext -layout` only to navigate and catch likely readings.
4. Transcribe into the existing poem file for that title.
5. Preserve lineation, stanza breaks, and visible ordinary-space indentation.
6. Normalize drop caps into ordinary text.
7. Continue multipage poems in one file and record full scan and printed spans.
8. Mark `status: "transcribed"` only after image checking.
9. Update the checklist in `volumes/01_early_works/books/02_the_dominant_city_1911_1912/book.md`.
10. Remove temporary rendered page images after verification.
11. Run the skill improvement loop and update reusable skills if the work
    exposes a repeated command, missing rule, or verification gap.

## Structural Reading For Later Framing

Use this section only when drafting editorial apparatus, not while transcribing.

_The Dominant City_ is Fletcher's early urban pressure chamber. The volume moves
from city-as-night and advertisement glare, through pleasure, industrial ruin,
moonlit exhaustion, civic apocalypse, anarchist fantasy, coal, sowing, and
prayer. It is less a London book than a machine for testing whether the city can
still be sung after the pastoral apparatus has failed.

Possible Sandbatch-facing editorial angles:

- city as Hollowing Engine before the term exists
- advertising hoardings as early dimensional reduction
- industrial London as anti-pastoral architecture
- night sequence as civic liturgy
- apocalyptic close as prayer after machinery

## Proposed Batches

### Batch 1: Opening City Poems

Render scans 13-22.

| Order | Poem | Printed pages | Scan pages |
| --- | --- | --- | --- |
| 001 | The Dominant City | 7 | 13 |
| 002 | The Hoardings | 8 | 14 |
| 003 | The Deserted Factory | 9-10 | 15-16 |
| 004 | The Evening Clouds | 11 | 17 |
| 005 | London Evening | 12 | 18 |
| 006 | Pleasure's Awakening | 13 | 19 |
| 007 | The Night of Pleasure | 14-16 | 20-22 |

### Batch 2: Night Sequence

Render scans 23-39.

| Order | Poem | Printed pages | Scan pages |
| --- | --- | --- | --- |
| 008 | Eros | 17-18 | 23-24 |
| 009 | Song of a Night | 19 | 25 |
| 010 | London at Night | 20-22 | 26-28 |
| 011 | In the City of Night | 23-25 | 29-31 |
| 012 | Tragic Night | 26 | 32 |
| 013 | Triumphant Night | 27 | 33 |
| 014 | The Hour of Peace | 28 | 34 |
| 015 | Saturday Night: Horses going to Pasture | 29 | 35 |
| 016 | The Great Moon | 30 | 36 |
| 017 | In the Night | 31 | 37 |
| 018 | From the Night to the Dawn | 32 | 38 |
| 019 | Dawn | 33 | 39 |

### Batch 3: Industrial and Transitional Poems

Render scans 40-57.

| Order | Poem | Printed pages | Scan pages |
| --- | --- | --- | --- |
| 020 | The Clouds | 34 | 40 |
| 021 | Factory Chimneys | 35 | 41 |
| 022 | Back Streets | 36 | 42 |
| 023 | Joy | 37 | 43 |
| 024 | The Age of Steel | 38 | 44 |
| 025 | Twilight | 39 | 45 |
| 026 | Chorus for the Tragedy of Man | 40-43 | 46-49 |
| 027 | Midwinter Moon | 44 | 50 |
| 028 | Dawn in Italy and in London | 45 | 51 |
| 029 | Saturday Night in Fleet Street | 46 | 52 |
| 030 | At the Meeting of the Days | 47 | 53 |
| 031 | The Banners | 48 | 54 |
| 032 | The Magician | 49 | 55 |
| 033 | The Forces at Work in the City | 50 | 56 |
| 034 | The Forging of the Sun | 51 | 57 |

### Batch 4: Closing City Cycle

Render scans 58-81.

| Order | Poem | Printed pages | Scan pages |
| --- | --- | --- | --- |
| 035 | Autumn Sunset | 52 | 58 |
| 036 | Two Autumn Dawns | 53-54 | 59-60 |
| 037 | An Autumn Picture | 55 | 61 |
| 038 | The City Lies at Ease Upon the Night | 56 | 62 |
| 039 | The Litanies of the City | 57-59 | 63-65 |
| 040 | The Death of the City | 60-63 | 66-69 |
| 041 | The Anarchist's Dream | 64-66 | 70-72 |
| 042 | Coal | 67-69 | 73-75 |
| 043 | The Sower | 70-73 | 76-79 |
| 044 | Epilogue: The Prayer | 74-75 | 80-81 |

## Verification

After transcription:

- Confirm all 44 poem files have `status: "transcribed"`.
- Confirm no poem has `source_pages_scan: null`.
- Confirm no poem body contains code fences, HTML entities, `<br>`, or visible
  page-break markers.
- Confirm the checklist in `book.md` has no unchecked poems.
- Record any damaged or uncertain readings in YAML `notes`.

