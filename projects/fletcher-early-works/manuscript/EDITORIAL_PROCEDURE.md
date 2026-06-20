# Editorial Procedure — Reading-Edition Poem Files

Project: The Early Works of John Gould Fletcher
Applies to: `manuscript/reading/<book>/**/*.md` files with `type: poem` or
`type: dedicatory-poem`
Established: 2026-06-10

## Purpose

The reading edition ("Edited and Arranged by C. Sandbatch") separates the
documentary witness from editorial judgment inside a single file per poem.
Each poem appears in markdown exactly once, with up to three sections.

## File Format

```markdown
---
title: '...'
type: poem            # required — OKF: every concept file carries a type
order: N
part: '...'
source: '../../../transcription/volumes/01_early_works/books/<book>/poems/<filename>.md'
---

## Original Lineation

<poem text exactly as transcribed from the source scan>

## Editorial Relineation        <- only when a relineation has been made

<the poem with editorial line- and stanza-break decisions applied>

## Context Notes                <- only when notes exist

Note: <editorial prose>
```

## Frontmatter Fields

Following the Open Knowledge Format (OKF) convention — each poem file is one
concept, identified by its path:

| Field | Required | Notes |
|---|---|---|
| `type` | Yes | Always `poem` (or `dedicatory-poem`). OKF requires every concept to carry a type. |
| `title` | Yes | Title as it appears in the source or editorial usage. |
| `order` | Yes | Integer sequence within the containing section directory. |
| `part` | When applicable | Part or book subdivision label (e.g. `'Book I: Fire'`). |
| `source` | Yes | Relative path from this file to the transcription witness in `transcription/volumes/`. Anchors the reading edition to its documentary source. |
| `tags` | Optional | Thematic and formal keywords. Deferred until editorial taxonomy established. |
| `description` | Optional | One-line editorial summary. Omit if not useful for navigation. |

The `source` path for a poem at `manuscript/reading/<book>/NNN_<name>.md` is:
```
../../../transcription/volumes/01_early_works/books/<transcription_book_dir>/poems/NNN_<name>.md
```
For poems in a subsection directory (e.g. `01_the_months_in_italy/`), add one
additional `../` at the start.

## Section Rules

### 1. Original Lineation (always present)

- Verbatim copy of the poem body from the documentary witness:
  `transcription/volumes/01_early_works/books/<book>/poems/<same filename>.md`
  (for dedicatory poems, the book's `front_matter/` file).
- Includes the source's print line-wraps (continuation lines indented four
  spaces), original punctuation, spelling, spaced ellipses (`. . .`), and
  irregular indentation.
- Never hand-edited. If the witness is corrected (against the scan), this
  section is updated to match the witness — never the other way around.

### 2. Editorial Relineation (only when warranted)

- Added only when the editor judges a form latent in the source print worth
  making explicit: resolving line wraps into full metrical lines, recovering
  stanza structure (e.g. a sonnet's quatrains and sestet), regularizing
  erratic indentation.
- **Lineation only. No verbal changes: no word, spelling, or punctuation
  may differ from the Original Lineation section.** Typographic normalization
  of spaced ellipses (`. . .` -> `...`) is the sole exception.
- If relineation is considered and declined, omit this section and record
  the refusal in Context Notes (see the April pattern below).

### 3. Context Notes (only when notes exist)

- First-person editorial prose, prefixed `Note:` (or `Notes:`). Three
  established classes:
  - **Refusal** — intervention considered and declined, with reason
    (April: "the symmetry of prospective stanzas did not permit an easy
    break, changes have not been imposed").
  - **Intervention defense** — rationale for a relineation that exercises
    real judgment (July: sonnet form made explicit).
  - **Retention defense** — a textual crux kept as printed, defended by
    precedent (August: "plash", with parallels from Eliot's The Spanish
    Gypsy and Aurobindo's Savitri).
- Routine work gets no note. Silence means "below the judgment threshold."
- **Never delete or rewrite an existing note.** Notes are the edition's
  decision log.

## Parsing Rule

Section boundaries are the literal H2 headings `## Original Lineation`,
`## Editorial Relineation`, `## Context Notes`. Any other heading inside a
section (e.g. a poem's internal `## I`, `## II` movements) is poem text,
not a section boundary.

## Workflow for an Editing Session

1. Pick a poem file. Confirm `## Original Lineation` matches the transcribe
   witness before working (regenerate it from the witness if in doubt).
2. If relineating: copy the Original section under a new
   `## Editorial Relineation` heading and change line/stanza breaks only.
3. If the decision involved judgment (intervention, refusal, or crux), add
   a `## Context Notes` section with a `Note:` explaining it.
4. Never edit the Original section by hand; never introduce verbal variants
   anywhere.

## Build Relationship (resolved 2026-06-10)

- The reading edition lives in `manuscript/reading/`, outside every
  build-written directory. Builds consume it read-only via
  `interior/collection.yaml` (`content_dir: ../manuscript/reading`) and
  write only under `interior/output/`.
- The parser understands this format: it typesets the Editorial Relineation
  when present, else the Original Lineation; Context Notes are captured to
  poem metadata (`context_notes`) and never typeset inline. Apparatus
  rendering of the notes is a future interior feature.
- The scaffold tool (`machinery/tools/scaffold_typeset_poems.py`) never
  overwrites existing reading files without `--force`.
- History: a regeneration pass overwrote all 273 content files on 2026-06-01
  and destroyed the inline notes then present, when this data still lived in
  the build tree. That failure class is closed by the layout above.

## State as of 2026-06-10 (after first full editorial pass)

- All 276 poems plus the Book of Nature dedicatory poem carry
  `## Original Lineation` synced to the witness (including the verified
  corrections: "piffling", Rome's dash normalization).
- **Editorial Relineation: 107 files.** 103 are routine wrap resolution
  (436 print-wrap continuations resolved volume-wide; word-break hyphens
  merged, compound hyphens kept), plus the four earlier hand-done files
  (March, July, August, the dedicatory poem). Three sonnets printed solid
  in the source were divided eight and six, each with an intervention
  note: From the Night to the Dawn (DC 018), Back Streets (DC 022),
  The Banners (DC 031).
- **Context Notes: 44 files** (after the second, contextual-commentary pass
  later the same day — see below). First pass, 25 files: refusals: April (B1 004), Epilogue to Two
  Days at Versailles (B1 073, thirteen lines on two rhymes), Tragic Night
  (DC 012). Crux/retention: plash (B1 009), respose (DC 015), ecstacies
  (FG 002). Context/allusion: June's "question" (B1 006), Messina
  (B1 021), Pindar's Akragas (B1 022), Syrinx (B1 023), the
  Summons/Poet's-Autumn variant pair (B1 035 + FW 034, cross-noted),
  Du Bellay (B1 051), theorbo/hautboy (B1 065), Et in Arcadia ego
  (B1 069), iron curtain (DC 026), Rimbaud's Voyelles + Bakst (FW 025),
  Alfred Stevens open question (FW 036), Keats (FW 042), Baudelaire's
  Le Couvercle (V 021), J. D. Fergusson (V 023), July's sonnet defense
  (B1 008).
- **Second pass (contextual commentary, same day): 19 more poems annotated
  in the quoted-precedent register** (the model is the August 'plash' note).
  Liturgical and classical: BCP burial sentence (B1 012), Horace's Soracte
  ode (B1 013), Catullus 85 (FW 029), Ecclesiastes (FG 037), Bromius/the
  Nine + Nietzsche's Birth of Tragedy (FW 028, two notes). English line:
  Shelley's skylark (B1 027), Blake's Tyger (FG 015), Villon via Rossetti
  (B1 039), James Thomson's City of Dreadful Night (DC 001). French line:
  Ronsard (B1 061), Hugo's sower and Millet (DC 043), Laforgue's moon
  (DC 016), Verhaeren's industrial epic (DC 024), Baudelaire four ways --
  Le Crepuscule du matin (DC 019), Les Litanies de Satan (V 001),
  L'Heautontimoroumenos (V 013), L'Albatros (V 014). Southern genealogy:
  Timrod's 'snow of Southern summers' against the 'grey snows of the
  Northland' (B1 056; Timrod quotation flagged for verification against a
  printed text). Form-history: the hokku adaptations dated against the
  Imagist association (V 024; originals an open research task).
  Quotations appear only where the editor is certain of the text; doubtful
  attributions are flagged in the note itself, never silently asserted.
- Source-given stanzas are never re-divided except where a note defends
  it; only solid-printed blocks were candidates.
- Part-subdirectory restructure (e.g. `01_the_months_in_italy/` with
  `00_section_title.md`) is begun but not completed; January (001) lives in
  the part directory, the rest of Book 1 at book level.
