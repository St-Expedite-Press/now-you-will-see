# John Gould Fletcher: The Complete Original Collections — Project Plan

Do not flatten Fletcher into the convenient museum label. That is the first rule.

This document is the consolidated working plan for _John Gould Fletcher: The
Complete Original Collections_ — a four-volume scholarly POD edition of
Fletcher's original poetry collections. It uses the Sandbatch register for
editorial architecture, but it keeps bibliographic claims, rights notes, source
facts, & tooling instructions documentary. The poems remain evidence. The plan
may have a voice.

## 1. Governing Thesis

Actually, the early Fletcher project is not a quaint apprentice shelf. It is the
place where the later Fletcher is still unstable enough to be useful: decorative,
embarrassing, lush, urban, synesthetic, self-financed, overbuilt, sometimes
terrible, sometimes suddenly exact. The point of the edition is to keep that
high-dimensionality available before the later labels arrive & reduce him to
"Imagist," "Southern poet," "Pulitzer winner," "regionalist," or any other
small administrative cage.

The local repository has a concrete publication object — a four-volume series:

- Series: _John Gould Fletcher: The Complete Original Collections_
- Vol. 1: _The Early Works of John Gould Fletcher_ — five 1913 London books
- Vol. 2: _The Dominant Works of John Gould Fletcher_ — four 1915-1918 books
- Vol. 3: _The Embattled Works of John Gould Fletcher_ — four 1921-1928 books
- Vol. 4: _The Falling Works of John Gould Fletcher_ — three 1935-1946 books
- Method: one Markdown file per poem or editorially defined poem-cycle
- Source base: full source PDFs preserved in `raw/`
- Status: Volume 1 first-pass transcription complete; Volumes 2-4 scaffolded

No no, this is important: the repo in hand is not yet the complete Fletcher
edition. Volume 1 is the engine. Build that engine correctly — verify,
apparatus, production — then the larger machine can inherit its method.

## 2. Current Repo State

The five early source PDFs are present, recorded, scaffolded, & transcribed.
The current local audit reports no structural transcription issues, no pending
poems, no unchecked checklist items, no forbidden markup hits, & no temporary
render files.

| Volume | Folder | Poems | Current status |
|---|---:|---:|---|
| _The Book of Nature, 1910-1912_ | `volumes/01_early_works/books/01_the_book_of_nature_1910_1912/` | 74 | transcribed |
| _The Dominant City (1911-1912)_ | `volumes/01_early_works/books/02_the_dominant_city_1911_1912/` | 44 | transcribed |
| _Fire and Wine_ | `volumes/01_early_works/books/03_fire_and_wine/` | 51 | transcribed |
| _Fool's Gold_ | `volumes/01_early_works/books/04_fools_gold/` | 67 | transcribed |
| _Visions of the Evening_ | `volumes/01_early_works/books/05_visions_of_the_evening/` | 40 | transcribed |

Total first-pass poem files: 276.

The next editorial state is not more transcription. It is verification,
normalization of apparatus, & conversion from working archive to publishable
edition.

The larger-source shelf has now begun: public-domain raw PDFs for the accessible
1915-1928 middle books have been added to `raw/`. _Branches of Adam_ remains the
major source acquisition gap. Permission for the late books is cleared; source
PDFs for _XXIV Elegies_, _South Star_, & _The Burning Mountain_ remain to be
acquired.

## 3. Source Base

All source PDFs stay unchanged in `raw/`. Stable names are already in place:

| Book | Source PDF | Pages | Local source note |
|---|---|---:|---|
| _The Book of Nature, 1910-1912_ | `raw/early_1913/the_book_of_nature_1910_1912.pdf` | 126 | Internet Archive scan |
| _The Dominant City (1911-1912)_ | `raw/early_1913/the_dominant_city_1911_1912.pdf` | 88 | Internet Archive scan |
| _Fire and Wine_ | `raw/early_1913/fire_and_wine.pdf` | 88 | Internet Archive scan |
| _Fool's Gold_ | `raw/early_1913/fools_gold.pdf` | 90 | user-supplied image-only PDF; title page locally confirms Max Goschen Ltd., London, 1913 |
| _Visions of the Evening_ | `raw/early_1913/visions_of_the_evening.pdf` | 56 | Internet Archive scan |
| _Irradiations: Sand and Spray_ | `raw/middle_1915_1928/irradiations_sand_and_spray.pdf` | 92 | Internet Archive scan |
| _Goblins and Pagodas_ | `raw/middle_1915_1928/goblins_and_pagodas.pdf` | 134 | Internet Archive scan |
| _Japanese Prints_ | `raw/middle_1915_1928/japanese_prints.pdf` | 120 | Internet Archive scan |
| _The Tree of Life_ | `raw/middle_1915_1928/the_tree_of_life.pdf` | 138 | Internet Archive scan |
| _Breakers and Granite_ | `raw/middle_1915_1928/breakers_and_granite.pdf` | 188 | Internet Archive scan |
| _Parables_ | `raw/middle_1915_1928/parables.pdf` | 164 | Internet Archive scan |
| _The Black Rock_ | `raw/middle_1915_1928/the_black_rock.pdf` | 202 | Internet Archive scan of authorized 1969 xerographic reprint; compare against first edition later |

The old planning dump treated _Fool's Gold_ publisher attribution as unresolved
because it relied on remote catalog ambiguity. The local source has now corrected
that problem for this repo: the title page governs.

## 4. Editorial Method

The editorial method is documentary first, literary second, institutional third.
Do the work in that order.

1. Preserve source PDFs unchanged.
2. Transcribe from page images, one scan page at a time.
3. Use OCR only for navigation & checking.
4. Preserve lineation, stanza breaks, visible indentation, & visible source
   hyphenation.
5. Normalize drop caps silently into ordinary first words.
6. Keep multipage poems in one poem file.
7. Keep source cycles in one poem file when the contents page presents them as
   one item with internal sections.
8. Record scan pages, printed pages, source PDF, book order, poem order, status,
   series, & notes in YAML.
9. Keep poem bodies free of code fences, HTML entities, `<br>`, & visible page
   break markers.
10. Separate textual notes from poem bodies.

The first-pass state is `transcribed`. The next required state is `checked`:
each poem re-opened against the scan image for title, first line, last line,
stanza count, page span, indentation, & uncertain characters. Final publication
requires a later `final` state after proofing.

## 5. Publication Architecture

### 5.1 Volume 1: The Early Works

_The Early Works of John Gould Fletcher_ is built as a single corpus edition
with five internal books. The sequence stays:

1. _The Book of Nature, 1910-1912_
2. _The Dominant City (1911-1912)_
3. _Fire and Wine_
4. _Fool's Gold_
5. _Visions of the Evening_

This order is editorially optimal rather than day-by-day guaranteed. All five
were issued in 1913; a fully certain month-by-month publication order has not
been established from the available local evidence.

### 5.2 Four-Volume Series Structure

The series divides the full Fletcher original-collections corpus into four
physical volumes:

| Vol | Title | Books | Period |
|---:|---|---:|---|
| 1 | _The Early Works of John Gould Fletcher_ | 5 | 1913 |
| 2 | _The Dominant Works of John Gould Fletcher_ | 4 | 1915–1918 |
| 3 | _The Embattled Works of John Gould Fletcher_ | 4 | 1921–1928 |
| 4 | _The Falling Works of John Gould Fletcher_ | 3 | 1935–1946 |

The four-volume split solves the old physical problem: the 1915-1928 middle
corpus is too large for a single POD hardback. Splitting it at 1918/1921 also
follows an intellectual boundary — the shift from the Imagist color-and-compression
mode to the larger, more embattled visionary and Southern-hinge books.

Quote-test each volume for trim, paper, binding, & vendor before commitment.
The full series page count is not yet known for Volumes 2-4.

## 6. Full Fletcher Corpus Map

This table consolidates the broader corpus planning from the old dump. It is a
working bibliography, not a final descriptive bibliography.

| Order | Title | Year | First publisher / place | Editorial role | Rights posture in U.S., 2026 |
|---:|---|---:|---|---|---|
| 1 | _The Book of Nature, 1910-1912_ | 1913 | Constable, London | early main text | public domain |
| 2 | _The Dominant City (1911-1912)_ | 1913 | M. Goschen, London | early main text | public domain |
| 3 | _Fire and Wine_ | 1913 | Grant Richards, London | early main text | public domain |
| 4 | _Fool's Gold_ | 1913 | Max Goschen Ltd., London | early main text | public domain |
| 5 | _Visions of the Evening_ | 1913 | Erskine Macdonald, London | early main text | public domain |
| 6 | _Irradiations: Sand and Spray_ | 1915 | Houghton Mifflin, Boston | dominant main text | public domain |
| 7 | _Goblins and Pagodas_ | 1916 | Houghton Mifflin, Boston | dominant main text | public domain |
| 8 | _Japanese Prints_ | 1918 | Four Seas Company, Boston | dominant main text; illustrated object | public domain |
| 9 | _The Tree of Life_ | 1918 | Chatto & Windus, London; possible New York issue to collate | dominant main text | public domain |
| 10 | _Breakers and Granite_ | 1921 | Macmillan, New York | embattled main text | public domain |
| 11 | _Parables_ | 1925 | Kegan Paul, Trench, Trubner, London | embattled main text; frontispiece | public domain |
| 12 | _Branches of Adam_ | 1926 | Faber and Gwyer, London | embattled main text; limited edition | public domain |
| 13 | _The Black Rock_ | 1928 | Macmillan, New York | embattled closing text | public domain |
| 14 | _XXIV Elegies_ | 1935 | Writers' Editions, Santa Fe | falling main text | permission cleared |
| 15 | _South Star_ | 1941 | Macmillan, New York | falling main text | permission cleared |
| 16 | _The Burning Mountain_ | 1946 | E. P. Dutton, New York | falling main text | permission cleared |

## 7. Volume Argument

### 7.1 Early

The early volume is the London detonation: five books in one year, printed
across multiple publishers, self-financed or quasi-self-forced into the world
before an audience had made a proper slot for him. It is not "minor" because it
is immature. It is major because it shows the machinery before its casing goes
on.

_The Book of Nature_ gives the landscape threshold. _The Dominant City_ turns
the same pressure toward the modern city. _Fire and Wine_ pushes rhetoric,
music, decadence, & theatrical intensity nearly to breaking. _Fool's Gold_ is
the inward diagnostic book. _Visions of the Evening_ is already near the later
compressed, chromatic, Asian-inflected Fletcher.

### 7.2 Dominant

The dominant period is where the public label "Imagist" attaches, but the label
is too small. _Irradiations_ & _Goblins and Pagodas_ matter because they make
color, rhythm, & perception structural — the poems do not represent sensation,
they enact it. _Japanese Prints_ makes the book-object visual: form and
illustration are not decorative but load-bearing. _The Tree of Life_ starts
pushing the lyric sequence toward visionary architecture, a mode that will become
the ambition and the problem of the embattled years that follow.

### 7.3 Embattled

The embattled period names a triple war: Fletcher against the Imagist label that
had become a cage; Fletcher against the pull of the South before he was willing
to call it home; and Fletcher against himself — the deepest war, the one that
resolves only in the late collapse back to Arkansas.

_Breakers and Granite_ begins the Southern return before the official late phase.
_Parables_ & _Branches of Adam_ are the ambitious, unwieldy, underread books
that keep the middle Fletcher from becoming a postcard of Imagism. _The Black
Rock_ is the embattled closing text: the last stand before the resolution begins.

### 7.4 Falling

The falling volume is not decline as failure. It is descent as gravity:
Fletcher's late movement into place, Arkansas, memory, elegy, & the pressure of
the South. The triple war of the embattled years is over. The resolution has
come. _XXIV Elegies_, _South Star_, & _The Burning Mountain_ make the late case.

## 8. Rights & Permissions

This is a working rights note, not legal advice.

For U.S. publication in 2026, works first published before 1931 are generally in
the public domain. That covers the local early edition & the 1915-1928 middle
books. Works first published from 1923 through 1963 require renewal analysis
when they are not already old enough to have expired by the 95-year term.

Practical rights posture:

| Group | Action |
|---|---|
| 1913-1928 books | Use as public-domain source texts; check plate/frontispiece rights for reproduced images. |
| _XXIV Elegies_ | Permission cleared. Acquire source PDF before transcription. |
| _South Star_ | Permission cleared. Acquire source PDF before transcription. |
| _The Burning Mountain_ | Permission cleared. Acquire source PDF before transcription. |

Permissions research should begin with University of Arkansas Special
Collections, University of Arkansas Press, Yale Beinecke, & Arkansas Studies
repositories because Fletcher papers, estate traces, & late-source materials
are concentrated there.

## 9. Production Strategy

The early edition can be designed as a serious scholarly POD book. The complete
Fletcher series needs page-count testing before any vendor promise.

Recommended production path:

1. IngramSpark first for library/bookstore distribution, hardback viability, &
   broad metadata reach.
2. BookVault as the high-object backup for cloth, foil, dust jacket, endpaper,
   ribbon, & other book-art features.
3. Lulu as a direct-sale / alternate hardback channel.
4. KDP as an Amazon supplementary channel only; KDP hardback page limits make it
   a poor primary platform for the large middle volume.

Default design assumptions:

- Trim: 6 x 9 in. for the early volume; test 7 x 10 in. for the larger middle
  volume if needed.
- Interior: cream or other uncoated text stock.
- Binding: hardback with dust jacket for scholarly object; paperback only as a
  secondary reading format.
- ISBNs: publisher-owned ISBNs, not platform-supplied identifiers.
- Text engine: Markdown source -> Pandoc or equivalent print pipeline.
- Proofing: one physical proof before any public listing.

Do not let vendor convenience decide the architecture of the edition. Quote the
book; then decide what form the book can survive.

### 9.1 Working Page-Count Estimates

Based on first-edition physical extents from HathiTrust records. Finished
estimates assume 6 × 9 trim, 12/14pt body type, and light but real scholarly
apparatus. These are planning figures, not vendor quotes.

| Volume | Source-page base | Finished estimate |
|---|---:|---|
| I. _The Early Works_ | c. 405 pp. | 450–525 pp. |
| II. _The Dominant Works_ | c. 425–435 pp. | 500–600 pp. |
| III. _The Embattled Works_ | c. 590 pp. | 650–750 pp. |
| IV. _The Falling Works_ | c. 330–430 pp. (unverified) | 400–525 pp. |

Whole-set estimate with apparatus: **2,000–2,400 finished pages**; tight
apparatus may hold it to 1,950–2,200; full introductions, headnotes, source
notes, and bibliography would push to 2,200–2,500.

Volume III (_The Embattled Works_) is the physically largest at current
estimates. Quote-test 7 × 10 trim or a tighter apparatus before assuming
IngramSpark can absorb it at 6 × 9. Volume IV page counts remain uncertain
until source PDFs are in hand.

## 10. Repo Workflow

The current repo workflow is already sound:

- `raw/`: untouched source PDFs, organized by source class
- `volumes/`: four publication volume folders, each with `volume.md`,
  volume-level `front_matter/`, `books/`, and `back_matter/` subfolders
- `volumes/<volume>/books/<book>/`: book folders containing `book.md`,
  `book.json`, source `front_matter/`, source `back_matter/`, and `poems/`
- `metadata/`: source manifests, policies, publication order, transcription
  plans, source matter inventory, MCP planning
- `machinery/skills/`: repo-local workflow instructions
- `machinery/tools/`: deterministic helper scripts
- `project_plan/`: this consolidated project plan
- `SANDBATCH.md`: house editorial register

All deterministic Python tools run through the repo-local virtual environment:

```powershell
.\.venv\Scripts\python.exe machinery\tools\<script>.py ...
```

Tools accelerate inspection, mapping, audits, indexing, & cleanup. They do not
replace page-image review.

## 11. Immediate Workplan

1. Verification pass on all 276 early poem files.
   Output: status moves from `transcribed` to `checked`, with notes for any
   uncertainty.
2. Global textual notes pass.
   Output:
   [volumes/01_early_works/back_matter/textual_notes.md](../volumes/01_early_works/back_matter/textual_notes.md)
   becomes the running apparatus for Volume 1.
3. Front matter pass.
   Output:
   [volumes/01_early_works/front_matter/intro.md](../volumes/01_early_works/front_matter/intro.md)
   becomes a real introduction, using the Sandbatch register where appropriate.
4. Production pilot.
   Output: one proofable Markdown/PDF build for a representative section.
5. Larger-series research memo.
   Output: late-book rights status, source availability, & physical volume
   feasibility.

## 12. Research Agenda

Research should now be boring, exact, & useful. The romance is in the poems; the
apparatus needs to behave.

Priority questions:

- Can a fully certain publication order for the five 1913 books be established
  from trade lists, ads, reviews, deposit records, or publisher archives?
- Does _The Tree of Life_ have meaningful U.K./U.S. issue variance?
- Where are the cleanest first-edition copy-texts for _XXIV Elegies_, _South Star_, & _The Burning Mountain_?
- Where are the cleanest archival exemplars of the late books?
- Which Fletcher periodical printings should become variant witnesses?
- How should illustrated matter in _Japanese Prints_ & _Parables_ be reproduced
  or described?

## Appendix A. Local File Inventory

| Area | Purpose |
|---|---|
| `README.md` | public orientation to the repo |
| `AGENTS.md` | local routing rules for agents, skills, persona, tools |
| `SANDBATCH.md` | house persona for editorial/structural prose |
| `raw/early_1913/` | five preserved 1913 source PDFs |
| `raw/middle_1915_1928/` | acquired public-domain middle-period source PDFs |
| `raw/late_rights_pending/` | late books with cleared permission; source PDFs still to be acquired |
| `volumes/01_early_works/front_matter/` | Volume 1 editorial front matter |
| `volumes/01_early_works/back_matter/` | Volume 1 editorial back matter and apparatus |
| `volumes/01_early_works/books/01_*` through `05_*` | transcribed early source book files |
| `metadata/source_manifest.md` | PDF names, page counts, source notes |
| `metadata/source_matter_inventory.md` | source front/back matter scan inventory |
| `metadata/publication_order.md` | local early-book order |
| `metadata/editorial_policy.md` | transcription rules |
| `metadata/four_volume_order.md` | canonical four-volume book order |
| `metadata/transcription_plans/early/` | Volume 1 per-book transcription plans |
| `metadata/mcp_server_plan.md` | external research/collaboration server plan |
| `machinery/tools/` | deterministic Python helpers |
| `machinery/skills/` | reusable local workflows |

## Appendix B. Source & Copy-Text Notes

- Local early-book copy-texts are the PDFs in `raw/`.
- Remote catalog records remain useful for publication metadata, but local title
  pages govern local source facts.
- _Fool's Gold_ publisher is confirmed: Max Goschen Ltd., London, 1913 — from
  local title page inspection.
- _Branches of Adam_ (Faber and Gwyer, 1926) was a limited edition of 81
  numbered, signed copies. A copy census and spot collation across surviving
  copies is desirable before finalization.
- _The Tree of Life_ (1918) may have both a U.K. (Chatto & Windus) and a New
  York (Macmillan) issue; collation before copy-text selection is required.
- _The Black Rock_ current source is an authorized 1969 University Microfilms
  xerographic reprint. Acceptable as a working source; first-edition comparison
  required before transcription is finalized.
- Late books require archival copy selection before any transcription plan is
  credible. Permission is cleared for all three falling-volume books. Archival
  starting points: University of Arkansas Special Collections, Yale/Beinecke,
  CALS, Arkansas Studies.

## Appendix C. Rights Checklist

| Task | Status | Next action |
|---|---|---|
| Confirm public-domain status for 1913 books | structurally clear by date | record in final rights memo |
| Confirm public-domain status for 1915-1928 books | structurally clear by date | record in larger-series memo |
| _XXIV Elegies_ permission | cleared | acquire source PDF |
| _South Star_ permission | cleared | acquire source PDF |
| _The Burning Mountain_ permission | cleared | acquire source PDF |
| Estate / archive contact map | preliminary | build contact log |

## Appendix D. Production Vendor Notes

| Vendor | Best use | Constraint |
|---|---|---|
| IngramSpark | primary scholarly hardback & distribution path | quote-test dust jacket, trim, paper, & spine before commitment |
| BookVault | high-object hardback, cloth/foil/endpaper/ribbon possibilities | distribution path needs case-by-case confirmation |
| Lulu | alternate hardback/direct-sale path | not preferred as sole library-facing infrastructure |
| KDP | supplemental Amazon discoverability | hardback page-count & trim constraints make it unsuitable as primary series platform |

## Appendix E. Tooling Notes

Current deterministic helpers:

- `pdf_pages.py`: source inspection, page rendering, OCR/navigation text
- `page_map.py`: offset-based scan/printed page mapping after visual confirmation
- `audit_transcription.py`: poem metadata, forbidden markup, checklist, temp
  render audit
- `project_index.py`: heading/index inspection for consolidated planning docs
- `ia_source.py`: Internet Archive file inspection/download for known public
  source identifiers

Future useful helper:

- A build-audit tool for assembling all poems into one print manuscript and
  reporting heading order, duplicate titles, missing notes, & unexpected status
  values.

## Appendix F. External Research Sources

Core source links retained from the planning dump or refreshed during this
consolidation:

- Cornell Copyright Services, "Copyright Term and the Public Domain in the
  United States": <https://guides.library.cornell.edu/copyright/publicdomain>
- KDP print options: <https://kdp.amazon.com/en_US/help/topic/G201834180>
- KDP hardcover help: <https://kdp.amazon.com/en_US/help/topic/GAVW3FZZAKA2KY3B>
- IngramSpark distribution: <https://www.ingramspark.com/how-it-works/distribute>
- IngramSpark file creation guide:
  <https://myaccount.ingramspark.com/documents/IngramSpark%20File%20Creation%20Guide.pdf>
- IngramSpark title setup / jacketed hardcover note:
  <https://www.ingramspark.com/blog/how-to-set-up-a-title-with-ingramspark-part-1>
- BookVault bespoke options: <https://bookvault.app/bookvaultbespoke-is-here/>
- Project Gutenberg Fletcher author page:
  <https://www.gutenberg.org/ebooks/author/32529>
- Morgan Library record for _The Book of Nature_:
  <https://www.themorgan.org/printed-books/89908>
- University of Arkansas Press / Pageplace preview of Lucas Carpenter's
  _Selected Poems of John Gould Fletcher_:
  <https://api.pageplace.de/preview/DT0400.9781610753739_A49510798/preview-9781610753739_A49510798.pdf>
- Google Books record for Ben F. Johnson, _Fierce Solitude_:
  <https://books.google.com/books/about/Fierce_Solitude.html?id=P6taAAAAMAAJ>

Primary catalog/source URLs:

- _The Book of Nature_: <https://catalog.hathitrust.org/Record/008961900>
- _The Dominant City_: <https://catalog.hathitrust.org/Record/000435969>
- _Fire and Wine_: <https://catalog.hathitrust.org/Record/000484040>
- _Fool's Gold_: <https://catalog.hathitrust.org/Record/012411015>
- _Visions of the Evening_: <https://catalog.hathitrust.org/Record/007912830>
- _Irradiations_: <https://catalog.hathitrust.org/Record/000389974>
- _Goblins and Pagodas_: <https://catalog.hathitrust.org/Record/000389971>
- _Japanese Prints_: <https://catalog.hathitrust.org/Record/000389977>
- _The Tree of Life_: <https://catalog.hathitrust.org/Record/000389982>
- _Breakers and Granite_: <https://catalog.hathitrust.org/Record/000389963>
- _Parables_: <https://catalog.hathitrust.org/Record/006639666>
- _Branches of Adam_: <https://catalog.hathitrust.org/Record/006639664>
- _The Black Rock_: <https://catalog.hathitrust.org/Record/001020967>

Late-book archive/library sources:

- _XXIV Elegies_ (Arkansas/CALS holdings):
  <https://cals.bibliocommons.com/v2/search?page=3&query=Fletcher%2C+John&searchType=author>
- _South Star_ (CALS library record):
  <https://cals.bibliocommons.com/v2/record/S100C1185712>
- _The Burning Mountain_ (Arkansas Studies, Dutton 1946 holding):
  <https://arstudies.contentdm.oclc.org/digital/collection/biblio/id/24995/>

## Appendix G. Per-Book Editorial Notes

One note per book: copy-text recommendation, textual flags, material
description. Rights language assumes permission is cleared for all books.
All source references are to first-edition HathiTrust records unless otherwise
noted.

### G.1 The Book of Nature, 1910–1912 (1913)

**Copy-text**: first edition, Constable, London; HathiTrust record
`008961900`. Physical extent: x + 107 pp. Selected contents emphasize sea
pieces, seasonal lyrics, and landscape writing — the clearest natural-worldly
threshold to Fletcher's later image-based poetics. Establishes his sensory
vocabulary while revealing how much of the later modernist sharpness begins in
landscape attention rather than manifesto.

**Textual flag**: none identified beyond standard title-page state inspection.

### G.2 The Dominant City (1911–1912) (1913)

**Copy-text**: first edition, M. Goschen, London; HathiTrust record
`000435969`. Physical extent: 75 pp. An essential bridge-book: alongside
pastoral and twilight materials, Fletcher is already converting metropolitan
experience into compressed form. Contemporary notice by Pound locates this book
in the field of the modern city poem before the Imagist codification.

**Textual flag**: check against the American Verse Project transcription as a
reading witness (not copy-text) for omitted punctuation or minor variants.

### G.3 Fire and Wine (1913)

**Copy-text**: first edition, G. Richards, London; HathiTrust record
`000484040`. Physical extent: 75 pp. The most rhetorically high-temperature of
the early books — decadent, symbolic, tonal, and musically dense. Selected
contents cluster around "Love and Suspicion," "The Vowels," and "Clown's Song."
Editorially valuable as evidence that Fletcher's later formal experiments were
partly a reaction against his own lush beginnings.

**Textual flag**: no distinct revision history surfaced; low-risk copy-text.

### G.4 Fool's Gold (1913)

**Copy-text**: first edition, Max Goschen Ltd., London; HathiTrust record
`012411015`. Physical extent: 91 pp. Publisher attribution is confirmed from the
local title page. A strongly introspective and aphoristic volume; selected
contents include "Discontent," "Life," "Sorrow," "The Golden Demon,"
"Marriage." Editorially the most inward early book, preserving Fletcher's
self-diagnostic register before the middle-period turn to color and architecture.

**Textual flag**: publisher attribution resolved by local title page. No further
bibliographical ambiguity.

### G.5 Visions of the Evening (1913)

**Copy-text**: first edition, Erskine Macdonald, London; HathiTrust record
`007912830`. Physical extent: [4] + 43 pp. The 1913 book closest to the later
compressed, outward-looking, Asian-inflected Fletcher. Selected pieces include
"Invocation to Evening," "From the Japanese," and "From the Chinese." Editorially
valuable as the volume that closes the early shelf on imminent transformation
rather than mere apprenticeship.

**Textual flag**: none identified; likely low-risk copy-text.

### G.6 Irradiations: Sand and Spray (1915)

**Copy-text**: first edition, Houghton Mifflin, Boston; HathiTrust record
`000389974`. Physical extent: xiv + c. 60 pp. The indispensable Fletcher book
for any scholarly edition and the moment where apprenticeship becomes
programmatic experiment: color, free rhythm, and concentrated perception turn
into a recognizable modernist method. Work originally published in _Poetry_ and
_The Egoist_.

**Textual flag**: later reissue in _Preludes and Symphonies_ (removed from this
series) may preserve minor resetting or paratextual differences worth noting in
apparatus.

### G.7 Goblins and Pagodas (1916)

**Copy-text**: first edition, Houghton Mifflin, Boston; HathiTrust record
`000389971`. Physical extent: xxiv + 98 + [2] pp. Fletcher's developed theory
of color and his sequence structure are most fully on display here. Sections,
typographic spacing, and titles matter enough that a facsimile-derived
transcription is preferable to any born-digital reprint.

**Textual flag**: check against _Preludes and Symphonies_ reissue for
author-approved republication changes; note any paratextual differences in
apparatus.

### G.8 Japanese Prints (1918)

**Copy-text**: first edition, Four Seas Company, Boston; HathiTrust record
`000389977`. Physical extent: 94 pp. + plates. An illustrated book of c. 1,000
copies; vellum copies in limited issue. The plates and decorative matter are
integral to the book's argument — it is a text about visuality as much as verbal
compression. Editorially, reproducing or at least describing the illustrations
is important.

**Textual flag**: image-text relation needs recording in the apparatus. Prioritize
a Hathi copy sourced from the Library of Congress to best preserve plate
presentation.

### G.9 The Tree of Life (1918)

**Copy-text**: U.K. first edition, Chatto & Windus, London; HathiTrust record
`000389982`. Physical extent: viii + 127 + [1] pp. A visionary and
sequence-driven architecture that broadens Fletcher's imagistic achievements.
Both Carpenter's acknowledgments and later sources point to both a London Chatto
& Windus issue and a New York Macmillan issue.

**Textual flag**: U.K./U.S. issue relationship requires collation before copy-text
is finalized. This is an open bibliographic question.

### G.10 Breakers and Granite (1921)

**Copy-text**: first edition, Macmillan, New York; HathiTrust record
`000389963`. Physical extent: 5 preliminary leaves + 163 pp. The hinge book of
Fletcher's middle career: formally still a middle-period work but thematically
beginning the American and Southern gravity that will dominate the last phase.
Johnson's biography calls it the middle book that most treats Southern themes.

**Textual flag**: none identified beyond routine collation for later reprint
appearances.

### G.11 Parables (1925)

**Copy-text**: first edition, Kegan Paul, Trench, Trubner, London; HathiTrust
record `006639666`. Physical extent: xii + 143 pp. Includes woodcut frontispiece
by John J. A. Murphy. One of Fletcher's most ambitious and insufficiently
understood middle books; decisive turn away from concentrated image toward
religious, moral, and prophetic prose-poetic structure.

**Textual flag**: preserving the frontispiece and original sectional architecture
is required. Decision on reproduction or description of illustrated matter before
transcription planning.

### G.12 Branches of Adam (1926)

**Copy-text**: first edition, Faber and Gwyer, London; HathiTrust record
`006639664`. Physical extent: 81 pp. A limited edition of 81 numbered, signed
copies. Fletcher's most prophetic and theologically ambitious middle-period work;
Carpenter calls it the "epic" of the difficult late-1920s books.

**Textual flag**: limited signed edition. Copy census and spot collation across
surviving copies desirable. Check for later magazine or excerpt publication.
Source PDF not yet acquired.

### G.13 The Black Rock (1928)

**Copy-text**: first edition, Macmillan, New York; HathiTrust record
`001020967`. Physical extent: 187 pp. Current working source is an authorized
1969 University Microfilms xerographic reprint — acceptable working source;
first-edition comparison required before transcription is finalized. Carpenter
calls it "visionary"; contemporary and retrospective criticism treats it as a
major if underread culmination of the middle period.

**Textual flag**: collate against periodical appearances where feasible. Acquire
first-edition scan before final copy-text is set.

### G.14 XXIV Elegies (1935)

**Copy-text**: first edition, Writers' Editions, Santa Fe. No open full-view scan
yet acquired; source search open. Permission cleared. Took Fletcher many years
to compose; twenty-four poems associated with a gestation from 1914 to 1934.
Carpenter treats it as the book that completed Fletcher's transition into Southern
regionalism. Editorially a high-priority acquisition.

**Textual flag**: acquire archival or dealer-descended copy. Track prior
publication for individual elegies.

### G.15 South Star (1941)

**Copy-text**: first edition, Macmillan, New York; CALS library record. Permission
cleared. More than half consists of what Fletcher called "echoes." A revised
version of his Arkansas centennial poem is included. The clearest late Fletcher
book of regional allegiance: southernized in subject, retrospective in method,
arranged around memory, recurrence, and local history.

**Textual flag**: track prior publication for all pieces; document the revised
"Story of Arkansas" and any echoes with prior periodical printings.

### G.16 The Burning Mountain (1946)

**Copy-text**: first edition, E. P. Dutton, New York; Arkansas Studies ContentDM
holding. Permission cleared. Long poems about place and time: meditative,
geographically dispersed, retrospective. Fletcher's final poetic statement.

**Textual flag**: treat as textually sensitive given the late date and limited
surviving copies; check against any archival typescripts or correspondence in the
Fletcher Papers at University of Arkansas Special Collections.

## Appendix H. Secondary Bibliography

An annotated short-list of the most useful secondary sources for editorial
and contextual work. Primary catalog/archive records are in Appendix F.

**Carpenter, Lucas, ed. _Selected Poems of John Gould Fletcher_. Fayetteville:
University of Arkansas Press, 1988.**
The most useful single modern editorial gateway: preface and introduction map
Fletcher's career phases, list the major poetry books with publisher/place data,
and preserve evidence of an estate permissions chain in the late twentieth
century. Use as the first interpretive map, not as a substitute for first
editions. The 1988 introduction is the standard career periodization source.
Locator: <https://api.pageplace.de/preview/DT0400.9781610753739_A49510798/preview-9781610753739_A49510798.pdf>

**Carpenter, Lucas. _John Gould Fletcher and Southern Modernism_. Fayetteville:
University of Arkansas Press, 1990.**
The best book-length study for the late and middle Fletcher; argues against
flattening Fletcher as merely an Imagist. Essential reading for the _Embattled_
and _Falling_ volume arguments.
Locator: <https://catalog.hathitrust.org/Record/002058888>

**Johnson, Ben F. III. _Fierce Solitude: A Life of John Gould Fletcher_.
Fayetteville: University of Arkansas Press, 1994.**
Standard modern biography. The strongest single source for publication
circumstances, Fletcher's marriages and geography, and the late Arkansas years
that matter for _South Star_ and _The Burning Mountain_.
Locator: <https://www.uapress.com/product/fierce-solitude/>
Google Books: <https://books.google.com/books/about/Fierce_Solitude.html?id=P6taAAAAMAAJ>

**de Chasca, Edmund S. _John Gould Fletcher and Imagism_. Columbia: University
of Missouri Press, 1978.**
The major study of the specifically Imagist Fletcher. Remains indispensable for
_Irradiations_, _Goblins and Pagodas_, _Japanese Prints_, _The Tree of Life_,
and _Breakers and Granite_, even where later scholarship qualifies its scope.

**Stephens, Edna B. _John Gould Fletcher_. New York: Twayne, 1967.**
Compact literary-critical overview. Still useful for establishing the edition's
historiography; Carpenter cites it as a standard reference.

**Morton, Bruce. _John Gould Fletcher: A Bibliography_. 1979.**
Should be consulted directly to verify periodical appearances, reprints, and
issue states. The Hathi author record identifies it as a separate published work.

**Vizcaíno-Alemán, Marcos. "Currents: The Southwestern Poetry of John Gould
Fletcher…" 2014.**
Particularly valuable for re-evaluating the late Southwestern and Southern
Fletcher, including _South Star_. Useful to resist the critical habit of ending
Fletcher's significance with the Imagist books.

## Index

- Adam, _Branches of_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#73-embattled), [Appendix B](#appendix-b-source--copy-text-notes),
  [Appendix G](#appendix-g-per-book-editorial-notes)
- apparatus: [Editorial Method](#4-editorial-method), [Immediate Workplan](#11-immediate-workplan)
- archive contacts: [Rights & Permissions](#8-rights--permissions), [Appendix B](#appendix-b-source--copy-text-notes)
- _Black Rock_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#73-embattled), [Appendix B](#appendix-b-source--copy-text-notes),
  [Appendix G](#appendix-g-per-book-editorial-notes)
- BookVault: [Production Strategy](#9-production-strategy), [Appendix D](#appendix-d-production-vendor-notes)
- _Book of Nature_: [Current Repo State](#2-current-repo-state), [Source Base](#3-source-base),
  [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map), [Appendix G](#appendix-g-per-book-editorial-notes)
- _Breakers and Granite_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#73-embattled), [Appendix G](#appendix-g-per-book-editorial-notes)
- _Burning Mountain_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Rights & Permissions](#8-rights--permissions), [Appendix C](#appendix-c-rights-checklist),
  [Appendix G](#appendix-g-per-book-editorial-notes)
- Carpenter, Lucas: [Appendix H](#appendix-h-secondary-bibliography)
- copy-text: [Editorial Method](#4-editorial-method), [Appendix B](#appendix-b-source--copy-text-notes),
  [Appendix G](#appendix-g-per-book-editorial-notes)
- copyright: [Rights & Permissions](#8-rights--permissions), [Appendix C](#appendix-c-rights-checklist),
  [Appendix F](#appendix-f-external-research-sources)
- _Dominant City_: [Current Repo State](#2-current-repo-state), [Source Base](#3-source-base),
  [Volume Argument](#71-early), [Appendix G](#appendix-g-per-book-editorial-notes)
- drop caps: [Editorial Method](#4-editorial-method)
- embattled: [Volume Argument](#73-embattled), [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map)
- _Fire and Wine_: [Current Repo State](#2-current-repo-state), [Source Base](#3-source-base),
  [Volume Argument](#71-early), [Appendix G](#appendix-g-per-book-editorial-notes)
- _Fool's Gold_: [Current Repo State](#2-current-repo-state), [Source Base](#3-source-base),
  [Appendix B](#appendix-b-source--copy-text-notes), [Appendix G](#appendix-g-per-book-editorial-notes)
- _Goblins and Pagodas_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#72-dominant), [Appendix G](#appendix-g-per-book-editorial-notes)
- IngramSpark: [Production Strategy](#9-production-strategy), [Appendix D](#appendix-d-production-vendor-notes)
- _Irradiations_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#72-dominant), [Appendix G](#appendix-g-per-book-editorial-notes)
- _Japanese Prints_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#72-dominant), [Appendix G](#appendix-g-per-book-editorial-notes)
- Johnson, Ben F.: [Appendix H](#appendix-h-secondary-bibliography)
- KDP: [Production Strategy](#9-production-strategy), [Appendix D](#appendix-d-production-vendor-notes)
- lineation: [Editorial Method](#4-editorial-method)
- Lulu: [Production Strategy](#9-production-strategy), [Appendix D](#appendix-d-production-vendor-notes)
- MCP: [Repo Workflow](#10-repo-workflow), [Appendix A](#appendix-a-local-file-inventory)
- page counts: [Production Strategy](#91-working-page-count-estimates)
- _Parables_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Volume Argument](#73-embattled), [Appendix G](#appendix-g-per-book-editorial-notes)
- production: [Production Strategy](#9-production-strategy), [Appendix D](#appendix-d-production-vendor-notes)
- rights: [Rights & Permissions](#8-rights--permissions), [Appendix C](#appendix-c-rights-checklist)
- Sandbatch: [Governing Thesis](#1-governing-thesis), [Repo Workflow](#10-repo-workflow)
- secondary bibliography: [Appendix H](#appendix-h-secondary-bibliography)
- _South Star_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Rights & Permissions](#8-rights--permissions), [Appendix C](#appendix-c-rights-checklist),
  [Appendix G](#appendix-g-per-book-editorial-notes)
- source PDFs: [Source Base](#3-source-base), [Appendix A](#appendix-a-local-file-inventory)
- textual flags: [Appendix G](#appendix-g-per-book-editorial-notes)
- transcription status: [Current Repo State](#2-current-repo-state)
- _Tree of Life_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Research Agenda](#12-research-agenda), [Appendix B](#appendix-b-source--copy-text-notes),
  [Appendix G](#appendix-g-per-book-editorial-notes)
- verification: [Editorial Method](#4-editorial-method), [Immediate Workplan](#11-immediate-workplan)
- _Visions of the Evening_: [Current Repo State](#2-current-repo-state), [Source Base](#3-source-base),
  [Volume Argument](#71-early), [Appendix G](#appendix-g-per-book-editorial-notes)
- _XXIV Elegies_: [Full Fletcher Corpus Map](#6-full-fletcher-corpus-map),
  [Rights & Permissions](#8-rights--permissions), [Appendix C](#appendix-c-rights-checklist),
  [Appendix G](#appendix-g-per-book-editorial-notes)

