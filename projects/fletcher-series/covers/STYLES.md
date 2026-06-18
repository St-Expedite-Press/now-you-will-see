---
document: typesetting-styles
version: "1.1"
project: "John Gould Fletcher: The Complete Original Collections"
publisher: "St. Expedite Press"
editor: "C. Sandbatch"
color_mode: black-and-white
formats:
  - hardcover
  - paperback
trim_sizes:
  hardcover: "6Ã—9 in"
  paperback: "5.5Ã—8.5 in"
pipeline: "Markdown â†’ Pandoc â†’ XeLaTeX â†’ PDF"
regimes:
  A: creole-small-press
  B: imagist-score
  C: apparatus-edition
  D: devotional-arc
active_regime: A
---

# Typesetting Styles
## John Gould Fletcher: The Complete Original Collections
### St. Expedite Press â€” Black-and-White Edition Specification

Four typesetting regimes are defined below, each with full specifications for
both the hardcover (6Ã—9 in) and paperback (5.5Ã—8.5 in) formats. All regimes
are black-and-white only. Volume differentiation that was previously carried
by accent colors is now carried by ornamental device assignment (see Â§ 3) and,
where applicable, rule weight variation.

Set `active_regime` in the YAML front matter above before beginning any
production work. StyleAgent reads this field to determine which regime governs
the current build.

---

## How to Use This Document

**For humans:** Read the regime section that matches `active_regime`. The
geometry block gives margins and text-block dimensions for LaTeX setup. The
role table gives size, leading, style, alignment, and tracking for every
typographic element. The B&W Adaptations section gives device and rule
assignments that replace the color elements from the design sessions.

**For agents:** Parse the YAML front matter to identify `active_regime`. Read
the matching `geometry` YAML block to extract margin and text-block values for
the `geometry` LaTeX package. Read the role table for the matching regime to
look up any role by code. Refer to Â§ 3 for the volume device assignment. Do not
mix elements from different regime sections. If `active_regime: null`, invoke
the regime-selection procedure in `machinery/skills/typesetting/SKILL.md`.

**Pandoc/LaTeX target:** XeLaTeX via Pandoc. Load typefaces with `fontspec`.
Use the `geometry` package for margins. Use `setspace` or manual
`\baselineskip` for leading. Use `titlesec` for heading formatting. Use
`fancyhdr` for running heads and page numbers. Template files live in
`machinery/tools/templates/` and are named `regime_{a|b|c|d}_{hc|pb}.tex`.

---

## 1. Shared Baseline

```yaml
shared:
  stock: "cream/natural uncoated text, 60â€“70 lb"
  binding_primary: "perfect-bound hardback with dust jacket"
  binding_secondary: "perfect-bound paperback"
  vendor_primary: IngramSpark
  vendor_secondary: BookVault
  isbn: publisher-owned
  trim_hardcover: {w_in: 6.0, h_in: 9.0}
  trim_paperback: {w_in: 5.5, h_in: 8.5}
  ingramspark_min_inner_hc_over500pp: 1.000in
  ingramspark_min_inner_pb_over500pp: 0.875in
  color: black-and-white
  spot_color: none
```

---

## 2. Typographic Role Taxonomy

All roles that require a typographic assignment in this edition. The `Code`
column is used in all regime role tables. The `Layer` column groups roles for
template organization.

| Code | Role | Layer |
|---|---|---|
| PB | Poem body (main text) | Poem |
| PT | Poem title (H1) | Poem |
| PS | Poem section heading (H2 â€” cycle poems) | Poem |
| BT | Book title (each of 16 source books) | Book |
| BP | Book part label | Book |
| VT | Volume title | Volume |
| ST | Series title | Volume |
| AN | Author name (title page) | Volume |
| ED | Editor credit | Volume |
| HT | Half-title page | Front matter |
| CP | Copyright / permissions block | Front matter |
| DED | Dedication | Front matter |
| EP | Epigraph text | Front matter |
| EPA | Epigraph attribution | Front matter |
| IT | Introduction / essay title | Front matter |
| IH2 | Introduction subheading (H2) | Front matter |
| IH3 | Introduction sub-subheading (H3) | Front matter |
| IB | Introduction / essay body | Front matter |
| NT | Note on the text (typography note) | Front matter |
| HOD | HODIE invocation â€” line 1 | St. Expedite |
| HOD2 | HODIE invocation â€” line 2 (*He chose today.*) | St. Expedite |
| HOD3 | HODIE invocation â€” line 3 (*Saint ExpÃ©dit, priez pour nous.*) | St. Expedite |
| OCL | *Omnia hodie* / closing line | St. Expedite |
| NOV | Novena text (Vol IV, Regime D only) | St. Expedite |
| PROV | Source provenance line (Regime B footer only) | St. Expedite |
| TNA | Textual notes section title | Back matter |
| TNEP | Textual notes section epigraph | Back matter |
| TNB | Textual notes body | Back matter |
| TNS | Textual notes subheading | Back matter |
| VAR | Variant / collation records (monospace â€” Regime C only) | Back matter |
| BIB | Bibliography entry | Back matter |
| IDX | Index entry | Back matter |
| IDXS | Index subentry | Back matter |
| COL | Colophon | Back matter |
| RHV | Running head â€” verso | Navigation |
| RHR | Running head â€” recto | Navigation |
| RFV | Running foot â€” verso (Regime D only) | Navigation |
| RFR | Running foot â€” recto (Regime D only) | Navigation |
| PN | Page number | Navigation |
| MST | Margin strip â€” English title (Regime B only) | Navigation |
| MSF | Margin strip â€” French translation (Regime B only) | Navigation |
| TCV | TOC â€” volume level entry | Navigation |
| TCB | TOC â€” book level entry | Navigation |
| TCP | TOC â€” poem level entry | Navigation |
| TCN | TOC â€” page number | Navigation |
| ORN | Ornamental device (crossroads / wave / gladius / star) | Structure |
| HRL | Horizontal rule | Structure |
| CAP | Caption (source image reproductions) | Structure |

---

## 3. B&W Volume Device Assignment

Replaces the four-color devotional arc across all regimes. One device per
volume, used at book openings, HODIE threshold positions, and section closers
where applicable. All devices: minimal line art, 8 pt, black, centered.

```yaml
volume_devices:
  I:
    name: Crossroads
    spirit: "Papa Legba â€” threshold, beginning"
    strokes: 4
    description: "4-stroke cross; the locus of Legba/Carrefour"
  II:
    name: Wave
    spirit: "La SirÃ¨ne â€” water, the tidal mode"
    strokes: 3
    description: "3 descending horizontal strokes"
  III:
    name: Gladius
    spirit: "St. Expedite / Ogou â€” arrival, the soldier's decision"
    strokes: 3
    description: "Roman gladius sword silhouette in 3 strokes"
  IV:
    name: Star
    spirit: "South Star / return to place"
    strokes: 8
    description: "8-pointed compass rose"
```

---

## 4. Active Regime

Set the value in the front-matter `active_regime` field before production:

```
active_regime: A   # creole-small-press
active_regime: B   # imagist-score
active_regime: C   # apparatus-edition
active_regime: D   # devotional-arc
```

Once set, all template work, LaTeX configuration, and typesetting decisions use
that regime only. To change regimes, update this field and rebuild all
templates. Do not mix elements between regimes without recording the deviation
in `metadata/`.

---

## Regime A â€” The Creole Small Press

**Argument:** A serious scholarly poetry edition made from a city with a
devotional visual culture. Classical and quiet in body and structure; charged
in ornament and threshold treatment. Cormorant Garamond throughout; justified;
generous margins; centered poem titles in small caps.

### Geometry

```yaml
regime_A:
  face: "Cormorant Garamond"
  apparatus_face: "Cormorant Garamond Italic"
  alignment: justified

  hardcover:
    trim: {w_in: 6.000, h_in: 9.000, w_pt: 432, h_pt: 648}
    margins:
      inner_in: 1.000
      outer_in: 1.250
      top_to_rh_in: 0.700
      top_to_text_in: 1.200
      foot_to_text_in: 1.100
      foot_to_pn_in: 0.700
    text_block: {w_in: 3.750, h_in: 6.700, w_pt: 270, h_pt: 482}
    body: {size_pt: 11.5, lead_pt: 16, lines_per_page: 30}
    running_head: {position: centered-top, size_pt: 8.0}
    page_number: {position: centered-foot, size_pt: 9.0}

  paperback:
    trim: {w_in: 5.500, h_in: 8.500, w_pt: 396, h_pt: 612}
    margins:
      inner_in: 0.875
      outer_in: 1.000
      top_to_rh_in: 0.550
      top_to_text_in: 0.900
      foot_to_text_in: 0.875
      foot_to_pn_in: 0.600
    text_block: {w_in: 3.625, h_in: 6.725, w_pt: 261, h_pt: 484}
    body: {size_pt: 11.0, lead_pt: 15, lines_per_page: 30}
    running_head: {position: centered-top, size_pt: 7.5}
    page_number: {position: centered-foot, size_pt: 8.5}
```

### Roles

Style codes: `roman` `italic` `bold` `sc` (small caps) `bold-sc` `bold-italic`
`old-fig` (old-style figures). Align codes: `justified` `fl` (flush left)
`centered` `fr` (flush right) `fl-hang` (flush left, hanging indent).

| Code | Role | HC pt | HC lead | PB pt | PB lead | Style | Align | Track |
|---|---|---|---|---|---|---|---|---|
| PB | Poem body | 11.5 | 16 | 11.0 | 15 | roman | justified | 0 |
| PT | Poem title | 11.5 | 16 | 11.0 | 15 | sc | centered | +0.08em |
| PS | Poem section heading | 10.0 | 14 | 9.5 | 14 | italic | centered | 0 |
| BT | Book title | 14.0 | 19 | 13.0 | 18 | roman | centered | 0 |
| BP | Book part label | 10.0 | 14 | 9.5 | 13 | sc | centered | +0.06em |
| VT | Volume title | 20.0 | 26 | 17.0 | 22 | roman | centered | 0 |
| ST | Series title | 9.0 | 13 | 8.5 | 12 | sc | centered | +0.10em |
| AN | Author name | 18.0 | 24 | 16.0 | 21 | roman | centered | 0 |
| ED | Editor credit | 9.0 | 13 | 8.5 | 12 | italic | centered | 0 |
| HT | Half-title | 16.0 | 22 | 14.0 | 19 | roman | centered | 0 |
| CP | Copyright block | 8.0 | 12 | 7.5 | 11 | roman | fl | 0 |
| DED | Dedication | 11.0 | 16 | 10.5 | 15 | italic | centered | 0 |
| EP | Epigraph text | 10.5 | 15 | 10.0 | 14.5 | italic | centered | 0 |
| EPA | Epigraph attribution | 8.5 | 12 | 8.0 | 11.5 | sc | centered | +0.06em |
| IT | Intro / essay title | 16.0 | 22 | 14.0 | 19 | roman | centered | 0 |
| IH2 | Intro subheading | 11.5 | 16 | 11.0 | 15 | bold-sc | fl | +0.06em |
| IH3 | Intro sub-subheading | 11.5 | 16 | 11.0 | 15 | italic | fl | 0 |
| IB | Intro / essay body | 11.5 | 16 | 11.0 | 15 | roman | justified | 0 |
| NT | Note on text | 10.0 | 14.5 | 9.5 | 14 | roman | justified | 0 |
| HOD | HODIE (colophon closer) | 9.0 | â€” | 9.0 | â€” | bold-sc | centered | +0.12em |
| TNA | Textual notes title | 13.0 | 18 | 12.0 | 17 | sc | centered | +0.08em |
| TNB | Textual notes body | 8.5 | 12 | 8.0 | 11.5 | italic | justified | 0 |
| TNS | Textual notes subheading | 8.5 | 12 | 8.0 | 11.5 | bold-sc | fl | +0.06em |
| BIB | Bibliography entry | 9.0 | 13.5 | 8.5 | 12.5 | roman | fl-hang | 0 |
| IDX | Index entry | 8.5 | 12 | 8.0 | 11.5 | roman | fl | 0 |
| IDXS | Index subentry | 8.5 | 12 | 8.0 | 11.5 | roman | fl | 0 |
| COL | Colophon | 8.5 | 13 | 8.0 | 12 | roman | centered | 0 |
| RHV | Running head â€” verso | 8.0 | â€” | 7.5 | â€” | sc | centered | +0.10em |
| RHR | Running head â€” recto | 8.0 | â€” | 7.5 | â€” | sc | centered | +0.10em |
| PN | Page number | 9.0 | â€” | 8.5 | â€” | old-fig | centered-foot | 0 |
| TCV | TOC â€” volume | 11.0 | 16 | 10.5 | 15 | roman | fl | 0 |
| TCB | TOC â€” book | 10.0 | 14.5 | 9.5 | 14 | italic | fl | 0 |
| TCP | TOC â€” poem | 9.0 | 13 | 8.5 | 12.5 | roman | fl | 0 |
| TCN | TOC â€” page number | 9.0 | 13 | 8.5 | 12.5 | old-fig | fr | 0 |
| ORN | Ornamental device | 8.0 | â€” | 8.0 | â€” | black | centered | â€” |
| HRL | Horizontal rule | 0.75pt | â€” | 0.75pt | â€” | â€” | full-measure | â€” |
| CAP | Caption | 8.0 | 11.5 | 7.5 | 11 | italic | centered | 0 |

### B&W Adaptations

**Book title rule:** 0.75pt black rule beneath BT, full measure, all volumes.

**Volume differentiation:** Volume device (Â§ 3) centered below BT rule on
book-opening pages. No rule-weight variation â€” device is the sole differentiator.

**HODIE:** Bold spaced small caps, 9pt, centered. 0.5pt rule 4pt above and 4pt
below. Last line of each volume colophon only.

**In-poem section breaks:** Wave device (7pt, black) for all volumes.

---

## Regime B â€” The Imagist Score

**Argument:** The white space is not empty â€” it is structurally constitutive.
Text lives in a narrow flush-left column facing a field of silence. Every poem
line occupies a fixed-height slug; the white within short-line slugs is the
duration between images. The series compresses as it falls.

### Geometry

```yaml
regime_B:
  face: "EB Garamond"
  alignment: fl-rag
  silence_column: true
  margin_strip: true

  hardcover:
    trim: {w_in: 6.000, h_in: 9.000, w_pt: 432, h_pt: 648}
    margins:
      inner_in: 0.850
      outer_in: 1.500
      top_to_text_in: 1.100
      foot_to_text_in: 1.000
    text_block: {w_in: 3.650, h_in: 6.900, w_pt: 263, h_pt: 497}
    silence_col: {w_in: 1.500, w_pt: 108}
    running_head: none-on-poem-pages
    page_number: {position: outer-margin-foot, size_pt: 7.5}
    margin_strip: {w_in: 0.5, orientation: rotated-90-bottom-to-top, size_pt: 6.5}

  paperback:
    trim: {w_in: 5.500, h_in: 8.500, w_pt: 396, h_pt: 612}
    margins:
      inner_in: 0.875
      outer_in: 1.125
      top_to_text_in: 0.900
      foot_to_text_in: 0.875
    text_block: {w_in: 3.500, h_in: 6.725, w_pt: 252, h_pt: 484}
    silence_col: {w_in: 1.125, w_pt: 81}
    running_head: none-on-poem-pages
    page_number: {position: outer-margin-foot, size_pt: 7.0}
    margin_strip: {w_in: 0.4, orientation: rotated-90-bottom-to-top, size_pt: 6.0}
    note: "At 3.5in / 10.5pt, longest rhymed Vol I lines may overflow slug.
           Acceptable within the regime's formal argument."

  slug_grid:
    body_size_pt: 11.0
    paperback_body_size_from_vol_II: 10.5
    volumes:
      I:   {hc_slug_pt: 15.0, pb_slug_pt: 14.5, hc_lines: 33, pb_lines: 29}
      II:  {hc_slug_pt: 14.5, pb_slug_pt: 14.0, hc_lines: 34, pb_lines: 30}
      III: {hc_slug_pt: 14.0, pb_slug_pt: 13.5, hc_lines: 35, pb_lines: 31}
      IV:  {hc_slug_pt: 13.5, pb_slug_pt: 13.0, hc_lines: 37, pb_lines: 33}
```

**French margin-strip translations (press-made, declared in NT):**

| Book | English | French |
|---|---|---|
| The Book of Nature | *The Book of Nature* | *Le Livre de la Nature* |
| The Dominant City | *The Dominant City* | *La CitÃ© dominante* |
| Fire and Wine | *Fire and Wine* | *Feu et Vin* |
| Fool's Gold | *Fool's Gold* | *L'Or des fous* |
| Visions of the Evening | *Visions of the Evening* | *Visions du Soir* |

Volumes IIâ€“IV translations follow the same pattern; see SKILL.md for
generation guidance.

### Roles

| Code | Role | HC pt | HC lead | PB pt | PB lead | Style | Align | Track |
|---|---|---|---|---|---|---|---|---|
| PB | Poem body | 11.0 | fixed-slug | 10.5 | fixed-slug | roman | fl-rag | 0 |
| PT | Poem title | 10.0 | 15 | 9.5 | 14 | italic | fl | 0 |
| PS | Poem section heading | 9.5 | 14 | 9.0 | 13 | sc | fl | +0.06em |
| BT | Book title | 13.0 | 18 | 12.0 | 17 | spaced-sc | fl | +0.12em |
| BP | Book part label | 9.0 | 13 | 8.5 | 12.5 | spaced-sc | fl | +0.08em |
| VT | Volume title | 18.0 | 24 | 16.0 | 21 | roman | fl | 0 |
| ST | Series title | 9.0 | 13 | 8.5 | 12 | italic | centered | 0 |
| AN | Author name | 16.0 | 22 | 14.0 | 19 | roman | fl | 0 |
| ED | Editor credit | 8.5 | 12 | 8.0 | 11.5 | italic | fl | 0 |
| HT | Half-title | 14.0 | 20 | 13.0 | 18 | roman | centered | 0 |
| CP | Copyright block | 8.0 | 12 | 7.5 | 11 | roman | fl | 0 |
| DED | Dedication | 10.5 | 15 | 10.0 | 14.5 | italic | fl | 0 |
| EP | Epigraph text | 10.0 | 14.5 | 9.5 | 14 | italic | fl | 0 |
| EPA | Epigraph attribution | 8.0 | 12 | 7.5 | 11 | roman | fl | 0 |
| IT | Intro / essay title | 14.0 | 20 | 13.0 | 18 | roman | fl | 0 |
| IH2 | Intro subheading | 11.0 | 15 | 10.5 | 15 | bold | fl | 0 |
| IH3 | Intro sub-subheading | 11.0 | 15 | 10.5 | 15 | italic | fl | 0 |
| IB | Intro / essay body | 11.0 | 15 | 10.5 | 15 | roman | fl-rag | 0 |
| NT | Note on text | 9.5 | 14 | 9.0 | 13.5 | roman | fl-rag | 0 |
| HOD | HODIE foot-mark (silence col) | 8.0 | â€” | 7.5 | â€” | bold-sc | silence-col-foot | +0.12em |
| PROV | Source provenance line | 7.0 | â€” | 6.5 | â€” | italic | fl | 0 |
| MST | Margin strip â€” English | 6.5 | â€” | 6.0 | â€” | roman | rotated-90 | +0.04em |
| MSF | Margin strip â€” French | 6.5 | â€” | 6.0 | â€” | italic | rotated-90 | 0 |
| TNA | Textual notes title | 12.0 | 17 | 11.0 | 16 | spaced-sc | fl | +0.10em |
| TNB | Textual notes body | 9.0 | 13 | 8.5 | 12.5 | roman | fl-rag | 0 |
| TNS | Textual notes subheading | 9.0 | 13 | 8.5 | 12.5 | bold | fl | 0 |
| BIB | Bibliography entry | 9.0 | 13 | 8.5 | 12.5 | roman | fl-hang | 0 |
| IDX | Index entry | 8.5 | 12 | 8.0 | 11.5 | roman | fl | 0 |
| IDXS | Index subentry | 8.5 | 12 | 8.0 | 11.5 | roman | fl | 0 |
| COL | Colophon | 8.5 | 13 | 8.0 | 12 | roman | fl | 0 |
| PN | Page number | 7.5 | â€” | 7.0 | â€” | old-fig | outer-margin-foot | 0 |
| TCV | TOC â€” volume | 11.0 | 16 | 10.5 | 15 | roman | fl | 0 |
| TCB | TOC â€” book | 10.0 | 14.5 | 9.5 | 14 | italic | fl | 0 |
| TCP | TOC â€” poem | 8.5 | 12.5 | 8.0 | 12 | roman | fl | 0 |
| TCN | TOC â€” page number | 8.5 | 12.5 | 8.0 | 12 | old-fig | fr | 0 |
| ORN | Wave device (all volumes) | 7.0 | â€” | 7.0 | â€” | black | centered | â€” |
| CAP | Caption | 7.5 | 11 | 7.0 | 10.5 | italic | fl | 0 |

### B&W Adaptations

**HODIE foot-mark:** Bold spaced small caps, 8pt (HC) / 7.5pt (PB), in silence
column at foot of text block. Book-opening pages only â€” one mark per book,
then silence.

**Margin strip differentiation:** English line in roman; French line in italic.
0.3pt rule between the two lines. No further treatment needed.

**Volume differentiation:** Slug compression per volume is the primary
differentiator. Additionally, each volume's Â§ 3 device appears in the silence
column at its HODIE position on book-opening pages.

**In-poem section breaks:** Wave device (7pt, black) for all volumes including
Vol II, where it previously matched the cobalt accent.

---

## Regime C â€” The Apparatus Edition with Devotional Markings

**Argument:** The poem and its documentary history are both present on the same
page, divided by a heavy black rule. Neither stream is subordinate. The
apparatus is not a supplement â€” it is simultaneous.

### Geometry

```yaml
regime_C:
  face: "TeX Gyre Pagella"
  apparatus_monospace: "Courier Prime"
  alignment: justified
  dual_stream: true

  hardcover:
    trim: {w_in: 6.000, h_in: 9.000, w_pt: 432, h_pt: 648}
    margins:
      inner_in: 1.000
      outer_in: 1.100
      top_to_rh_in: 0.650
      top_to_text_in: 1.100
      foot_to_text_in: 1.000
    text_block: {w_in: 3.900, h_in: 6.900, w_pt: 281, h_pt: 497}
    running_head: {position: centered-top, size_pt: 8.0}
    page_number: {position: outer-header, size_pt: 8.5}
    body: {size_pt: 10.5, lead_pt: 14, lines_per_page: 35}
    apparatus:
      dividing_rule_pt: 2.5
      prose_col_w_in: 2.700
      prose_col_w_pt: 194
      gutter_w_in: 0.120
      variant_col_w_in: 1.080
      variant_col_w_pt: 78
      prose_size_pt: 8.5
      prose_lead_pt: 12
      variant_size_pt: 7.5
      variant_lead_pt: 11
      min_poem_stream_pct: 33

  paperback:
    trim: {w_in: 5.500, h_in: 8.500, w_pt: 396, h_pt: 612}
    margins:
      inner_in: 0.875
      outer_in: 0.900
      top_to_rh_in: 0.550
      top_to_text_in: 0.875
      foot_to_text_in: 0.875
    text_block: {w_in: 3.725, h_in: 6.750, w_pt: 268, h_pt: 486}
    running_head: {position: centered-top, size_pt: 7.5}
    page_number: {position: outer-header, size_pt: 8.0}
    body: {size_pt: 10.0, lead_pt: 13, lines_per_page: 35}
    apparatus:
      dividing_rule_pt: 2.5
      prose_col_w_in: 2.600
      prose_col_w_pt: 187
      gutter_w_in: 0.100
      variant_col_w_in: 1.025
      variant_col_w_pt: 74
      prose_size_pt: 8.0
      prose_lead_pt: 11.5
      variant_size_pt: 7.0
      variant_lead_pt: 10.5
      min_poem_stream_pct: 33
```

### Roles

Poem title alignment is mode-dependent: `centered` for rhymed / metrically
regular poems; `fl` for free verse. Declare the mode in the poem Markdown
source with a metadata field `poem_mode: [rhymed|free]` and resolve in the
LaTeX template.

| Code | Role | HC pt | HC lead | PB pt | PB lead | Style | Align | Track |
|---|---|---|---|---|---|---|---|---|
| PB | Poem body | 10.5 | 14 | 10.0 | 13 | roman | justified | 0 |
| PT (rhymed) | Poem title â€” rhymed | 10.5 | 14 | 10.0 | 13 | sc | centered | +0.06em |
| PT (free) | Poem title â€” free verse | 10.5 | 14 | 10.0 | 13 | sc | fl | +0.06em |
| PS | Poem section heading | 9.5 | 14 | 9.0 | 13 | italic-sc | follows PT | +0.04em |
| BT | Book title | 13.0 | 18 | 12.0 | 17 | sc | centered | +0.08em |
| BP | Book part label | 9.5 | 14 | 9.0 | 13 | spaced-sc | centered | +0.08em |
| VT | Volume title | 16.0 | 22 | 14.5 | 20 | bold-sc | centered | +0.06em |
| ST | Series title | 9.0 | 13 | 8.5 | 12 | sc | centered | +0.10em |
| AN | Author name | 16.0 | 22 | 14.5 | 20 | roman | centered | 0 |
| ED | Editor credit | 9.0 | 13 | 8.5 | 12 | italic | centered | 0 |
| HT | Half-title | 14.0 | 20 | 13.0 | 18 | roman | centered | 0 |
| CP | Copyright block | 8.0 | 12 | 7.5 | 11 | roman | fl | 0 |
| DED | Dedication | 10.0 | 15 | 9.5 | 14 | italic | centered | 0 |
| EP | Epigraph text | 10.0 | 14.5 | 9.5 | 14 | italic | centered | 0 |
| EPA | Epigraph attribution | 8.5 | 12 | 8.0 | 11.5 | sc | centered | +0.06em |
| IT | Intro / essay title | 14.0 | 20 | 13.0 | 18 | roman | centered | 0 |
| IH2 | Intro subheading | 10.5 | 14 | 10.0 | 13 | bold-sc | fl | +0.06em |
| IH3 | Intro sub-subheading | 10.5 | 14 | 10.0 | 13 | italic | fl | 0 |
| IB | Intro / essay body | 10.5 | 14 | 10.0 | 13 | roman | justified | 0 |
| NT | Note on text | 9.5 | 14 | 9.0 | 13 | roman | justified | 0 |
| HOD | HODIE colophon closer | 11.0 | â€” | 11.0 | â€” | bold-sc | centered | +0.12em |
| OCL | *Omnia hodie* book closer | 8.0 | â€” | 8.0 | â€” | bold-italic | centered | 0 |
| TNA | Textual notes title | 12.0 | 17 | 11.0 | 16 | sc | centered | +0.10em |
| TNEP | Apparatus section epigraph | 9.0 | 13 | 8.5 | 12 | italic | centered | 0 |
| TNB | Textual notes body | 8.5 | 12 | 8.0 | 11.5 | roman | justified | 0 |
| TNS | Textual notes subheading | 8.5 | 12 | 8.0 | 11.5 | bold-sc | fl | +0.06em |
| VAR | Variant / collation records | 7.5 | 11 | 7.0 | 10.5 | mono | fl | 0 |
| BIB | Bibliography entry | 9.0 | 13 | 8.5 | 12.5 | roman | fl-hang | 0 |
| IDX | Index entry | 8.5 | 12 | 8.0 | 11.5 | roman | fl | 0 |
| IDXS | Index subentry | 8.5 | 12 | 8.0 | 11.5 | roman | fl | 0 |
| COL | Colophon | 8.5 | 13 | 8.0 | 12 | roman | centered | 0 |
| RHV | Running head â€” verso | 8.0 | â€” | 7.5 | â€” | sc | centered | +0.10em |
| RHR | Running head â€” recto | 8.0 | â€” | 7.5 | â€” | sc | centered | +0.10em |
| PN | Page number | 8.5 | â€” | 8.0 | â€” | old-fig | outer-header | 0 |
| TCV | TOC â€” volume | 11.0 | 15 | 10.5 | 14.5 | bold-sc | fl | +0.06em |
| TCB | TOC â€” book | 10.0 | 14 | 9.5 | 13.5 | italic | fl | 0 |
| TCP | TOC â€” poem | 8.5 | 12.5 | 8.0 | 12 | roman | fl | 0 |
| TCN | TOC â€” page number | 8.5 | 12.5 | 8.0 | 12 | old-fig | fr | 0 |
| ORN | Book-opening device | 8.0 | â€” | 8.0 | â€” | black | centered | â€” |
| HRL | Dividing rule (apparatus) | 2.5pt | â€” | 2.5pt | â€” | black | full-measure | â€” |
| CAP | Caption | 7.5 | 11 | 7.0 | 10.5 | italic | centered | 0 |

### B&W Adaptations

**Dividing rule (HRL):** 2.5pt black rule, full measure, all four volumes.
Previously alizarin; black rule of this weight retains authority without color.

**TNEP apparatus epigraph (*Ossa arida audite verbum Domini*):** Bold italic,
9pt, centered. Optionally enclosed in a 0.5pt box rule (6pt inset all sides)
for visual separation without color.

**HODIE (HOD):** Bold spaced small caps, 11pt, centered. 0.5pt rules above and
below. Last line of each volume colophon only.

***Omnia hodie* (OCL):** Bold italic, 8pt, centered. End of every book section.
Previously in alizarin; the bold italic carries the weight.

**Double Dealer tint (Vol III variant column):** 6% black screen behind VAR
column. Barely perceptible; marks the Vol III apparatus as inhabiting the
1921â€“1926 New Orleans little-magazine world.

**Volume differentiation:** The 2.5pt black rule (HRL) is constant â€” it
provides no volume distinction. Differentiation is carried by the Â§ 3 volume
device at book openings only.

---

## Regime D â€” The Devotional Arc

**Argument:** The series has a shape: a descent. The page tightens across four
volumes. The reader who reads all four in sequence has registered the
compression in their body before recognizing it as a formal decision.

### Geometry

```yaml
regime_D:
  face: "Gentium Plus"
  alignment: justified
  running_position: foot

  hardcover:
    trim: {w_in: 6.000, h_in: 9.000, w_pt: 432, h_pt: 648}
    margins:
      inner_in: 1.000
      outer_in: 1.300
      top_to_text_in: 1.100
      foot_to_text_in: 1.250
      running_foot_from_bottom_in: 0.700
    text_block: {w_in: 3.700, h_in: 6.650, w_pt: 266, h_pt: 479}
    running_foot: {position: centered-foot, size_pt: 7.5, style: spaced-italic}
    page_number: {position: in-running-foot-string, size_pt: 7.5}
    body_size_pt: 12

  paperback:
    trim: {w_in: 5.500, h_in: 8.500, w_pt: 396, h_pt: 612}
    margins:
      inner_in: 0.875
      outer_in: 1.100
      top_to_text_in: 0.875
      foot_to_text_in: 1.000
      running_foot_from_bottom_in: 0.650
    text_block: {w_in: 3.525, h_in: 6.625, w_pt: 254, h_pt: 477}
    running_foot: {position: centered-foot, size_pt: 7.0, style: spaced-italic}
    page_number: {position: in-running-foot-string, size_pt: 7.0}
    body_size_pt: 11

  leading_per_volume:
    note: "Leading decreases 1pt per volume in each format.
           Cumulative compression across series: ~17%."
    hardcover:
      I:   {lead_pt: 18, lines_per_page: 26}
      II:  {lead_pt: 17, lines_per_page: 28}
      III: {lead_pt: 16, lines_per_page: 29}
      IV:  {lead_pt: 15, lines_per_page: 31}
    paperback:
      I:   {lead_pt: 17, lines_per_page: 27}
      II:  {lead_pt: 16, lines_per_page: 29}
      III: {lead_pt: 15, lines_per_page: 30}
      IV:  {lead_pt: 14, lines_per_page: 33}

  book_title_rule_weight:
    note: "B&W volume differentiation at book-opening pages.
           Rule beneath BT (code HRL in Regime D). Arc: thin â†’ heavy â†’ thin."
    I:   {weight_pt: 0.50, reading: thin}
    II:  {weight_pt: 1.00, reading: medium}
    III: {weight_pt: 1.50, reading: heavy}
    IV:  {weight_pt: 0.50, reading: thin-return}

  gladius_end_mark:
    code: ORN-G
    size_pt: 6
    position: centered-after-last-line
    applies_to: closing-poem-of-each-book-section
    color: black
    note: "Frequency increases across Vol IV â€” marks the accumulation of
           arrivals in the late Fletcher corpus."
```

### Roles

Running foot format: `[vol title] Â· [page number] Â· [book title]`
in 7.5pt (HC) / 7pt (PB) spaced italic, centered at foot.

| Code | Role | HC pt | HC lead | PB pt | PB lead | Style | Align | Track |
|---|---|---|---|---|---|---|---|---|
| PB | Poem body | 12.0 | per-vol | 11.0 | per-vol | roman | justified | 0 |
| PT | Poem title | 12.0 | â€” | 11.0 | â€” | bold-italic | fl | 0 |
| PS | Poem section heading | 11.0 | 16 | 10.0 | 15 | italic | fl | 0 |
| BT | Book title | 16.0 | 22 | 14.0 | 19 | roman | centered | 0 |
| BP | Book part label | 10.0 | 14.5 | 9.5 | 14 | bold-sc | fl | +0.08em |
| VT | Volume title | 20.0 | 27 | 17.0 | 23 | roman | centered | 0 |
| ST | Series title | 9.5 | 14 | 9.0 | 13 | roman | centered | +0.08em |
| AN | Author name | 18.0 | 25 | 16.0 | 22 | roman | centered | 0 |
| ED | Editor credit | 9.0 | 13 | 8.5 | 12 | italic | centered | 0 |
| HT | Half-title | 16.0 | 22 | 14.0 | 19 | roman | centered | 0 |
| CP | Copyright block | 8.0 | 12 | 7.5 | 11 | roman | fl | 0 |
| DED | Dedication | 11.0 | 17 | 10.5 | 16 | italic | centered | 0 |
| EP | Epigraph text | 10.5 | 16 | 10.0 | 15 | italic | centered | 0 |
| EPA | Epigraph attribution | 8.5 | 12 | 8.0 | 11.5 | roman | centered | +0.04em |
| IT | Intro / essay title | 16.0 | 23 | 14.0 | 20 | roman | centered | 0 |
| IH2 | Intro subheading | 12.0 | 17 | 11.0 | 16 | bold | fl | 0 |
| IH3 | Intro sub-subheading | 12.0 | 17 | 11.0 | 16 | italic | fl | 0 |
| IB | Intro / essay body | 12.0 | 17 | 11.0 | 16 | roman | justified | 0 |
| NT | Note on text | 10.5 | 15.5 | 10.0 | 15 | roman | justified | 0 |
| HOD | HODIE â€” line 1 | 10.0 | â€” | 9.5 | â€” | bold-sc | centered | +0.14em |
| HOD2 | HODIE â€” line 2 | 8.0 | â€” | 7.5 | â€” | roman | centered | 0 |
| HOD3 | HODIE â€” line 3 | 8.0 | â€” | 7.5 | â€” | bold-italic | centered | 0 |
| NOV | Novena (Vol IV only) | 10.5 | 16 | 10.0 | 15 | italic | fr | 0 |
| TNA | Textual notes title | 13.0 | 19 | 12.0 | 18 | sc | centered | +0.10em |
| TNB | Textual notes body | 9.5 | 14 | 9.0 | 13.5 | roman | justified | 0 |
| TNS | Textual notes subheading | 9.5 | 14 | 9.0 | 13.5 | bold | fl | 0 |
| BIB | Bibliography entry | 9.5 | 14 | 9.0 | 13.5 | roman | fl-hang | 0 |
| IDX | Index entry | 9.0 | 13 | 8.5 | 12.5 | roman | fl | 0 |
| IDXS | Index subentry | 9.0 | 13 | 8.5 | 12.5 | roman | fl | 0 |
| COL | Colophon | 9.0 | 13.5 | 8.5 | 12.5 | roman | centered | 0 |
| RFV | Running foot â€” verso | 7.5 | â€” | 7.0 | â€” | spaced-italic | centered | +0.04em |
| RFR | Running foot â€” recto | 7.5 | â€” | 7.0 | â€” | spaced-italic | centered | +0.04em |
| PN | Page number | 7.5 | â€” | 7.0 | â€” | old-fig | in-foot-string | 0 |
| TCV | TOC â€” volume | 12.0 | 18 | 11.0 | 16.5 | roman | fl | 0 |
| TCB | TOC â€” book | 10.5 | 16 | 10.0 | 15 | italic | fl | 0 |
| TCP | TOC â€” poem | 9.0 | 13.5 | 8.5 | 12.5 | roman | fl | 0 |
| TCN | TOC â€” page number | 9.0 | 13.5 | 8.5 | 12.5 | old-fig | fr | 0 |
| ORN-G | Gladius end-mark | 6.0 | â€” | 6.0 | â€” | black | centered | â€” |
| ORN-W | Wave device (section break) | 7.0 | â€” | 7.0 | â€” | black | centered | â€” |
| HRL | Book title rule (per vol) | per-vol | â€” | per-vol | â€” | black | full-measure | â€” |
| CAP | Caption | 8.0 | 11.5 | 7.5 | 11 | italic | centered | 0 |

### B&W Adaptations

**HODIE (three-line invocation):** Line 1 in bold spaced small caps (weight
carries the authority). Line 2 in roman. Line 3 (*Saint ExpÃ©dit, priez pour
nous.*) in bold italic. All black â€” the typographic weight differentiation
replaces the color register of the original design.

**Novena (Vol IV, NOV):** Bold italic, flush right, full black. The flush-right
alignment and italic register distinguish it from all other front-matter
elements without color.

**Book title rule (HRL):** Varies per volume per `book_title_rule_weight` in
the geometry block above. This is the primary B&W volume differentiator in
Regime D alongside leading variation.

**Gladius end-mark (ORN-G):** Black throughout. Accumulation across Vol IV is
legible in black â€” ink is sufficient.

---

## Cross-Regime Comparison

```yaml
comparison:
  A_creole_small_press:
    face: "Cormorant Garamond"
    hc_body: "11.5 / 16pt"
    pb_body: "11.0 / 15pt"
    hc_margins: "inner 1.0 / outer 1.25 / top 1.2 / foot 1.1"
    hc_text_block: "3.75 Ã— 6.70 in"
    pb_margins: "inner 0.875 / outer 1.0 / top 0.9 / foot 0.875"
    pb_text_block: "3.625 Ã— 6.725 in"
    alignment: justified
    vol_differentiator: "device (Â§3)"
    running_position: centered-top-head
    distinctive: "crossroads ornament; generous symmetric margins"

  B_imagist_score:
    face: "EB Garamond"
    hc_body: "11 / fixed-slug (15â€“13.5pt by vol)"
    pb_body: "10.5 / fixed-slug (14.5â€“13pt by vol)"
    hc_margins: "inner 0.85 / outer 1.5 / top 1.1 / foot 1.0"
    hc_text_block: "3.65 Ã— 6.90 in"
    pb_margins: "inner 0.875 / outer 1.125 / top 0.9 / foot 0.875"
    pb_text_block: "3.50 Ã— 6.725 in"
    alignment: fl-rag
    vol_differentiator: "slug compression; device in silence column"
    running_position: outer-margin-strip-rotated-90
    distinctive: "silence column; bilingual margin strip; no running heads on poem pages"

  C_apparatus_edition:
    face: "TeX Gyre Pagella"
    hc_body: "10.5 / 14pt"
    pb_body: "10.0 / 13pt"
    hc_margins: "inner 1.0 / outer 1.1 / top 1.1 / foot 1.0"
    hc_text_block: "3.90 Ã— 6.90 in"
    pb_margins: "inner 0.875 / outer 0.9 / top 0.875 / foot 0.875"
    pb_text_block: "3.725 Ã— 6.75 in"
    alignment: justified
    vol_differentiator: "device (Â§3); Double Dealer tint Vol III"
    running_position: centered-top-head
    distinctive: "2.5pt black dividing rule; dual prose/monospace apparatus stream"

  D_devotional_arc:
    face: "Gentium Plus"
    hc_body: "12 / 15â€“18pt by vol"
    pb_body: "11 / 14â€“17pt by vol"
    hc_margins: "inner 1.0 / outer 1.3 / top 1.1 / foot 1.25"
    hc_text_block: "3.70 Ã— 6.65 in"
    pb_margins: "inner 0.875 / outer 1.1 / top 0.875 / foot 1.0"
    pb_text_block: "3.525 Ã— 6.625 in"
    alignment: justified
    vol_differentiator: "leading per vol; book-title rule weight per vol; device (Â§3)"
    running_position: centered-foot
    distinctive: "variable leading arc; gladius accumulation; HODIE threshold; novena Vol IV"
```

