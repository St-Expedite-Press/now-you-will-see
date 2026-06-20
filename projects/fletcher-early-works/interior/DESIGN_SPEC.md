# Design Specification — *The Early Works of John Gould Fletcher*

Decisions from the stylization session of 2026-06-18 (operator + C. Sandbatch
editorial register). This spec governs the typeset; the Royal style sheet
(`collection_royal.yaml`) and the proof templates implement it. Where a decision
requires a framework template change, it is flagged **[framework]**; project-local
changes are **[style sheet]** or **[content]**.

## 1. Edition & format

- **Single definitive edition.** No trade/softcover variants pursued.
- **Trim:** Royal 8vo — **6.14 × 9.21 in (156 × 234 mm)**, case-bound hardcover.
- **Paper:** crème stock, B&W. (Royal 8vo is the largest trim IngramSpark prints
  on crème; it is also the period-correct 1913 London octavo.)
- **Page furniture:** folio only, centered at the foot; **no running heads** on
  poem pages. No folios on display leaves (half-title, title, dividers, blanks).

## 2. Type

- **Body:** Crimson Pro. **Display** (dividers, title page, half-title):
  **Cormorant Garamond** (same Garamond idiom, display-cut). **[framework]**
- **Body size:** one **uniform** size, set to the **minimum required for the
  single widest verse line in the volume to fit whole** at the chosen measure.
  → ACTION: measure the longest verse line across all 276 poems, then derive the
  size. The measure is set as wide as the margins allow precisely to keep that
  size as large as possible. **[style sheet + measurement]**
- **Leading:** line_spread 1.15.
- **Hyphenation:** **never break a word in verse**; prose (intro, notes,
  afterword) hyphenates normally. **[framework]**

## 3. Verse layout

- **Placement:** short poems **top-set from a common sink** (titles land at the
  same height down the page); whitespace collects below. Not centered. **[framework]**
- **Stanza gap:** **one full blank line (~1.0 baselineskip)**, driven by a fixed
  `\interstanzaskip` — *after* the verse-glue fix below makes it the real lever.
- **Indentation:** quantize the editorial relineation's per-line indents to fixed
  em-steps (1em, 2em…) so all indented lines align to one grid. **[framework]**
- **Turned lines:** minimized by the wide-measure + uniform-min-size strategy
  above; the goal is effectively zero turned lines. Any residual turn hangs 2em. **[framework]**
- **Long poems (must flow):** break **only between stanzas**, and **never strand
  a single line** of a stanza at a page top/bottom (tightens the orphan rule that
  stranded the couplet on p.50). **[framework]**
- **Poem titles:** small caps (Crimson Pro). **[framework]**
- **Untitled / number-only poems:** small-cap roman numeral in the title slot. **[framework]**
- **Epigraphs:** italic, indented, reduced size; attribution in small caps. **[framework]**
- **Cycles / movements:** italic movement titles (named, or italic numeral). **[framework]**

## 4. Structure & dividers

- **Book / part dividers:** name only, centered on a recto, blank verso;
  Cormorant display. Austere — no ornament. **[framework]**
- **Per-book title pages:** book title **+ original 1913 imprint note**
  (publisher/printer for that book). → ACTION: gather the five imprints from the
  transcription front matter. **[content + framework]**
- **Named internal sequences** (e.g. *The Months in Italy*): **full-page
  sub-dividers**, name only, in a smaller register than book dividers. Wire the
  existing `01_the_months_in_italy` grouping. **[content + framework]**
- **Relineation transparency:** flag an intervention **only when substantive**
  (restored stanza, fixed stray line) via a context note; otherwise silent.

## 5. Front matter

- **Half-title:** yes — bare title on the first recto, **with the series line**
  ("Volume I of *The Complete Original Collections*"), blank verso. **[content/framework]**
- **Title page:** full imprint **+ editor credit** — title, subtitle,
  "John Gould Fletcher", "edited by C. Sandbatch", St. Expedite Press /
  Nouvelle Orleans / 2026. **[content/framework]**
- **Copyright page:** **full production statement** — public-domain notice for the
  1913 poems; editorial matter, relineation, and notes © 2026 C. Sandbatch /
  St. Expedite Press; first-edition line; printer; ISBN. **[content]**
- **Table of contents:** **books only** (five book titles + start pages). **[framework]**

## 6. Back matter

- **Endnotes:** keyed **by poem title + printed page, lemma-led** (open with a
  line citation `ll. 9–10 ('lemma'):` or `Form:`); grouped per book. Each book's
  notes open with a **section head** ("Notes to *Fire and Wine*"); folios run
  throughout; no running head. No reference marks in the verse. **[framework]**
- **Afterword ("The Specter at the North"):** typeset the existing **outline
  as-is**, marked provisional. **[content]**
- **Colophon:** press device **+ full production note** — set in Crimson Pro;
  Royal 8vo on crème, case-bound; edited by C. Sandbatch for St. Expedite Press,
  Nouvelle Orleans, 2026. **[content/framework]**
- **Decoration:** austere body throughout; the **single press device** appears on
  the colophon only.

## 7. Implementation order

1. **[framework] Verse-glue fix** — zero the per-stanza `verse` list glue
   (`\topsep`/`\partopsep`/`parskip`) so `\interstanzaskip` is the sole, real
   inter-stanza lever; set it to ~1.0\baselineskip. *Precondition for everything
   in §3.* Without it, stanza spacing is governed by accidental list glue.
2. **[measurement]** Longest-verse-line scan → set uniform body size + measure.
3. **[framework]** Display face (Cormorant), small-cap titles, top-set sink,
   em-step indents, no-verse-hyphenation, orphan rule, per-book notes heads,
   sub-divider support, TOC = books only.
4. **[content]** Per-book imprint notes, half-title series line, title/copyright/
   colophon text, afterword outline, wire Months-in-Italy sub-divider.
5. **[style sheet]** Update `collection_royal.yaml` to the resolved size/margins
   and any new display-font keys.
6. Rebuild → render the key leaves → visual review against this spec.
