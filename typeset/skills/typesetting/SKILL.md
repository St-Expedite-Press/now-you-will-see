# StyleAgent â€” Typesetting Skill

## Use When

The task involves any typesetting, layout, or production decision for the
edition:

- Selecting or confirming the active typesetting regime
- Building or adjusting Pandoc/LaTeX templates
- Specifying or verifying margins, type sizes, or leading
- Resolving a typographic question about a specific role (e.g., "what size is
  the book title in Regime C paperback?")
- Producing proof PDFs or preparing build configurations
- Writing or debugging Pandoc/LaTeX templates
- Generating vendor submission specs (IngramSpark, BookVault, Lulu, KDP)
- Identifying discrepancies between a rendered PDF and the spec

Do not use for: poem transcription, source intake, YAML poem metadata,
page-span verification, rights research, or editorial prose. If the task
combines typesetting with editorial voice, use the configured `PERSONA.md`
register for the prose and StyleAgent for the layout decisions.

## Reads

Before making any typesetting decision, read in full:

1. `projects/fletcher-complete-original-collections/covers/STYLES.md` â€” the authoritative specification. Contains all
   four regimes, both formats (HC 6Ã—9, PB 5.5Ã—8.5), all role sizes and
   leading, page geometry, B&W adaptations, and volume device assignment.
2. The user prompt.
3. `projects/fletcher-complete-original-collections/transcribe/project_plan/PROJECT_PLAN.md` Â§ 9 (Production Strategy and Â§ 9.1 Working
   Page-Count Estimates) for vendor and trim constraints.
4. `AGENTS.md` for routing context.

## Writes

- Pandoc/LaTeX template files (`.tex`) under the owning typeset template area, named
  `regime_{a|b|c|d}_{hc|pb}.tex`
- Geometry configuration blocks for direct use in LaTeX preambles
- Type specification summaries for vendor submission
- Production notes filed in `projects/fletcher-complete-original-collections/transcribe/metadata/` when a decision is durable and not
  derivable from STYLES.md alone

## Regime Selection Procedure

Read the `active_regime` field in the YAML front matter of `projects/fletcher-complete-original-collections/covers/STYLES.md`.

If `active_regime: null`:
1. Present the four regimes with their one-line formal arguments:
   - **A â€” The Creole Small Press:** Classical justified type with St. Expedite
     ornament; accessible to scholars and general readers; closest to
     conventional academic press design.
   - **B â€” The Imagist Score:** Flush-left ragged right; fixed-slug grid; wide
     silence column; most formally radical; strongest argument for the Imagist
     period; challenges Vol I rhymed forms productively.
   - **C â€” The Apparatus Edition:** Dual-stream page divided by 2.5pt rule;
     poem above, apparatus below; for editions where the textual history is as
     important as the reading experience.
   - **D â€” The Devotional Arc:** Variable leading decreasing across four
     volumes; gladius end-marks accumulating through Vol IV; HODIE threshold
     invocations; French novena in Vol IV; the edition as ritual object.
2. Ask the user to confirm a regime.
3. Once confirmed, update `active_regime` in `projects/fletcher-complete-original-collections/covers/STYLES.md` front
   matter.
4. Proceed with that regime only.

If `active_regime` is set, use it. Do not suggest alternatives unless asked.

## Format Selection

Both hardcover (HC, 6Ã—9 in) and paperback (PB, 5.5Ã—8.5 in) specs exist for
each regime in `STYLES.md`. Treat them as separate production targets sharing
one Markdown source. A decision that affects one format's template may need
reflection in the other.

IngramSpark minimum inside margins for volumes over 500 pages:
- Hardcover: 1.000 in
- Paperback: 0.875 in

All STYLES.md specs meet or exceed these minimums.

## Key Decisions This Agent Handles

**Margins and geometry**
- Extract `margins` and `text_block` from the active regime's YAML block
  for the `geometry` LaTeX package
- For Regime B: configure the silence column as a fixed right-margin reservation
- For Regime C: configure the dual-stream page with `minipage` or `paracol`

**Typeface loading**
- Regime A: `\setmainfont{Cormorant Garamond}`
- Regime B: `\setmainfont{EB Garamond}`
- Regime C: `\setmainfont{TeX Gyre Pagella}` â€” available as a LaTeX package;
  also loadable via fontspec as Palatino Linotype if available on system
- Regime D: `\setmainfont{Gentium Plus}`
- Regime C apparatus monospace: `\setmonofont{Courier Prime}`

**Leading configuration**
- Standard regimes (A, C): set `\baselineskip` from geometry `lead_pt` value
- Regime B: implement fixed-slug grid using a custom `\poemline` environment
  that sets `\vspace` to enforce slug height regardless of content height
- Regime D: `\baselineskip` must be set per-volume via a volume-level LaTeX
  command; define `\setvolumelead{I|II|III|IV}` that sets the correct value

**Role mapping to LaTeX commands**
- PB â†’ `\normalsize` in poem environment with `\baselineskip` from spec
- PT â†’ `\poemtitle` custom command
- PS â†’ `\poemsection` custom command
- BT â†’ `\booktitle` custom command
- BP â†’ `\bookpart` custom command
- VT â†’ `\volumetitle` custom command
- All display roles: define in preamble using `titlesec` or manual
  `\newcommand` with explicit `\fontsize{}{}\selectfont`

**Ornamental devices**
- Devices are placed as includegraphics calls to SVG/PDF art files in
  `covers/` or as Unicode characters if the face supports them
- The wave, crossroads, gladius, and star devices should be produced as
  separate minimal PDF/EPS files named `device_wave.pdf`, `device_cross.pdf`,
  `device_gladius.pdf`, `device_star.pdf` and stored with the owning cover or typeset assets
- The 2.5pt dividing rule in Regime C: use `\rule{\textwidth}{2.5pt}`

**B&W volume differentiation**
- Regime A and C: volume device only (Â§ 3 of STYLES.md)
- Regime B: slug-height compression is automatic per volume if leading is
  parameterized; additionally, the volume device appears in the silence column
- Regime D: book-title rule weight set from `book_title_rule_weight` in
  geometry; leading set from `leading_per_volume`

**Regime B margin strip**
- French translations are declared in `STYLES.md` for Vol I books
- For Vols IIâ€“IV, generate translations at the time of template construction
  and record them in `STYLES.md` under the Regime B section
- Strip is implemented as a `\marginpar` or side-note package positioned at
  the vertical center of the text block, with `\rotatebox{90}`

**Regime D novena**
- Full novena text (French, Creole Catholic version) is stored in
  a stage-owned LaTeX include
- It is inserted only on the verso of the Vol IV title page via a conditional
  in the template

## Vendor Submission Checklist

When preparing for a vendor submission, verify:

1. Trim size matches vendor options (IngramSpark supports 6Ã—9 and 5.5Ã—8.5)
2. All margins meet IngramSpark minimums for the volume's page count
3. Bleed: none needed for interior pages; 0.125 in bleed on cover files only
4. Color mode: black-and-white interior confirmed (no spot color declarations)
5. PDF standard: PDF/X-1a preferred for IngramSpark
6. Embedded fonts: all fonts fully embedded; verify with `pdffonts`
7. Page count: must be even; add blank page if needed
8. Physical proof ordered before any public listing

## Guardrails

- Do not alter source poem Markdown files for typesetting reasons.
- Do not change YAML poem metadata for typesetting reasons.
- Do not invent type sizes or margins not in STYLES.md without recording the
  deviation explicitly in `projects/fletcher-complete-original-collections/transcribe/metadata/` with a rationale.
- Do not mix elements from different regimes.
- Do not commit vendor-specific constraints as permanent spec changes without
  recording them in `projects/fletcher-complete-original-collections/transcribe/metadata/`.
- Do not set `active_regime` without explicit user confirmation.

