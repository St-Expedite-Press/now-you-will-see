# Fire and Wine Transcription Plan

## Source

- Volume: _Fire and Wine_
- Source PDF: `raw/early_1913/fire_and_wine.pdf`
- PDF pages: 88
- Status: present and safe to transcribe
- Persona boundary: neutral documentary transcription only. Do not use
  SandbatchAgent for poem bodies, YAML, page spans, verification, or cleanup.

## Page Map

The poem-body page map is visually confirmed from the title/contents/front
matter and first poem pages:

- printed page = scan page - 4
- scan page = printed page + 4

Expected body ranges:

- Book I: Fire: printed pages 13-37, scans 17-41
- Book II: Wine: printed pages 41-75, scans 45-79

## Front Matter

Unnumbered source front matter is recorded outside the poem sequence. It does
not count toward the 51 contents-listed poems.

| Order | Item | Matter type | Printed pages | Scan pages | File |
|---:|---|---|---|---|---|
| 1 | To Anyone Reading This Book | dedication | unnumbered | 9 | `volumes/01_early_works/books/03_fire_and_wine/front_matter/00_to_anyone_reading_this_book.md` |

## Contents and Source Spans

Use the contents page starts and the next poem start to determine ending pages.
Correct spans during transcription if page images contradict these expectations.

| Order | Poem | Part | Printed pages | Scan pages |
|---:|---|---|---|---|
| 1 | Spring Love | Book I: Fire | 13 | 17 |
| 2 | Midsummer Love | Book I: Fire | 14 | 18 |
| 3 | Autumnal Love | Book I: Fire | 15 | 19 |
| 4 | Midwinter Love | Book I: Fire | 16-17 | 20-21 |
| 5 | I Cannot Love You | Book I: Fire | 18 | 22 |
| 6 | Lacking Your Love | Book I: Fire | 19 | 23 |
| 7 | In the Year That Is Past | Book I: Fire | 20 | 24 |
| 8 | Could My Soul Dream | Book I: Fire | 21 | 25 |
| 9 | Eyes | Book I: Fire | 22 | 26 |
| 10 | Hands | Book I: Fire | 23 | 27 |
| 11 | Mystic Union | Book I: Fire | 24 | 28 |
| 12 | Song in the Desert | Book I: Fire | 25 | 29 |
| 13 | Love and Suspicion | Book I: Fire | 26 | 30 |
| 14 | The End of Love | Book I: Fire | 27 | 31 |
| 15 | The Icy Waters | Book I: Fire | 28 | 32 |
| 16 | In the Shadow of a Pine | Book I: Fire | 29 | 33 |
| 17 | A Prayer Answered | Book I: Fire | 30-31 | 34-35 |
| 18 | At Parting | Book I: Fire | 32 | 36 |
| 19 | The Mating | Book I: Fire | 33 | 37 |
| 20 | Love's Memory Fading | Book I: Fire | 34 | 38 |
| 21 | Love's Memory Forgotten | Book I: Fire | 35 | 39 |
| 22 | The End of Desire | Book I: Fire | 36 | 40 |
| 23 | The Final Futility | Book I: Fire | 37 | 41 |
| 24 | To My Mother | Book II: Wine | 41 | 45 |
| 25 | The Vowels | Book II: Wine | 42-43 | 46-47 |
| 26 | The Three Transformations of Poetry | Book II: Wine | 44 | 48 |
| 27 | The Hosts of Song | Book II: Wine | 45 | 49 |
| 28 | Dionysus and Apollo | Book II: Wine | 46 | 50 |
| 29 | The Poet's Character | Book II: Wine | 47 | 51 |
| 30 | The Poet's Desire | Book II: Wine | 48 | 52 |
| 31 | Poetic Art | Book II: Wine | 49 | 53 |
| 32 | On an Editor's Refusal of My Poems | Book II: Wine | 50 | 54 |
| 33 | To the Publisher Who Refused to Publish My Poems | Book II: Wine | 51 | 55 |
| 34 | The Poet's Autumn | Book II: Wine | 52 | 56 |
| 35 | The Poet's Immortality | Book II: Wine | 53 | 57 |
| 36 | Lines to the Admirers of Alfred Stevens | Book II: Wine | 54-55 | 58-59 |
| 37 | To the Public | Book II: Wine | 56 | 60 |
| 38 | Present-Day Poetry | Book II: Wine | 57 | 61 |
| 39 | Clown's Song | Book II: Wine | 58-59 | 62-63 |
| 40 | The Price of Poetry | Book II: Wine | 60 | 64 |
| 41 | Art's Sacrifices | Book II: Wine | 61 | 65 |
| 42 | Fatigue | Book II: Wine | 62 | 66 |
| 43 | The Dream of Art | Book II: Wine | 63-64 | 67-68 |
| 44 | A Distant Song | Book II: Wine | 65-66 | 69-70 |
| 45 | Dream-Poetry | Book II: Wine | 67 | 71 |
| 46 | Art | Book II: Wine | 68-69 | 72-73 |
| 47 | To the Muse | Book II: Wine | 70 | 74 |
| 48 | The Poet, I | Book II: Wine | 71 | 75 |
| 49 | Time and Poet | Book II: Wine | 72 | 76 |
| 50 | The Poet, II | Book II: Wine | 73-74 | 77-78 |
| 51 | The Triumph of Song | Book II: Wine | 75 | 79 |

## Batches

1. Scans 17-24: `Spring Love` through `In the Year That Is Past`.
2. Scans 25-35: `Could My Soul Dream` through `A Prayer Answered`.
3. Scans 36-45: `At Parting` through `To My Mother`.
4. Scans 46-55: `The Vowels` through `To the Publisher Who Refused to Publish My Poems`.
5. Scans 56-66: `The Poet's Autumn` through `Fatigue`.
6. Scans 67-79: `The Dream of Art` through `The Triumph of Song`.

## Method

- Render pages with `.\.venv\Scripts\python.exe machinery\tools\pdf_pages.py render`.
- Use OCR text only as navigation and a checking aid.
- Transcribe from rendered page images, one page at a time.
- Normalize drop caps silently.
- Preserve lineation, stanza breaks, and meaningful continuation indentation.
- Use `book_part: "Book I: Fire"` or `book_part: "Book II: Wine"`.
- Keep each contents item as one poem file unless the scan contradicts the
  scaffold.
- Set poem status to `transcribed` only after visual image checking.

## Verification

Run:

- `.\.venv\Scripts\python.exe machinery\tools\audit_transcription.py books\03_fire_and_wine`
- `rg 'status: "pending"|source_pages_scan: null|```|<br|&quot;|page-break|PAGE BREAK' books\03_fire_and_wine`
- `Get-ChildItem -Name tmp_fw*.png`

Acceptance criteria:

- 51 poem files.
- All statuses are `transcribed`.
- No missing scan spans.
- No unchecked checklist entries.
- No forbidden markup or visible page-break annotations.
- No temporary render files remain.
- `book.md` has `transcription_status: "transcribed"`.

