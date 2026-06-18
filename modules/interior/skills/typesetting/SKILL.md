---
name: typesetting
description: Configure and verify typeset builds using the texgraph render_config system. Use for collection.yaml setup, render_config parameter selection (trim size, margins, fonts, leading), PDF/X build verification, vendor submission checks, and template debugging. For content-type-specific decisions, load poetry or prose skill instead.
---

# Typesetting

## Use When

Load this skill when the typeset task is about layout configuration, build
verification, or production output — not content-type-specific formatting:

- Setting up or adjusting `collection.yaml` and `render_config`
- Choosing trim size and margin geometry for a print format
- Configuring fonts, base size, leading, or stanza spacing
- Debugging a failed LaTeX build
- Verifying PDF/X compliance and font embedding
- Preparing vendor submission specs

For verse layout decisions (stanza_skip, indentation, cycles), load
`modules/interior/skills/poetry/SKILL.md`. For prose layout, load
`modules/interior/skills/prose/SKILL.md`.

## Required Reads

- `projects/<project_id>/interior/collection.yaml` — current render_config
- `ONTOLOGY.md § Data Schemas` — full collection.yaml and render_config schema
- `ONTOLOGY.md § Command Surface` — build and watch commands

## render_config Reference

All geometry and typography is set in `collection.yaml` under `render_config`.
The full schema is in `ONTOLOGY.md § Data Schemas`. Common parameters:

| Key | Description | Common values |
|---|---|---|
| `fontsize` | Base type size | `10pt`, `11pt`, `12pt` |
| `mainfont` | OpenType font name (must be installed) | `EB Garamond`, `Cormorant Garamond` |
| `paperwidth` / `paperheight` | Trim size | See formats below |
| `top_margin` / `bottom_margin` | Page margins | `1in` standard |
| `inner_margin` | Gutter (binding) margin | `1in`; increase for thick books |
| `outer_margin` | Fore-edge margin | `0.75in` standard |
| `line_spread` | Leading multiplier | `1.1`–`1.2` |
| `stanza_skip` | Vertical space between stanzas | `1.2ex`–`1.8ex` |

### Adjusting inter-stanza spacing

`stanza_skip` is the single lever for the gap between a poem's stanzas. In the
proof pipeline it becomes the `\interstanzaskip` length (named to avoid the
`verse` package's internal `\stanzaskip`); change `stanza_skip` in the style
sheet to move every poem's stanza spacing at once. A single poem can override it
from its own front matter — `stanza_skip: 2ex` — scoped to that poem only:

```yaml
---
title: 'A Poem That Needs Air'
type: poem
order: 5
stanza_skip: 2.2ex   # looser stanza gaps for this poem only
---
```

## Standard Format Geometries

```yaml
# Trade paperback (5.5 x 8.5 in)
paperwidth: 5.5in
paperheight: 8.5in
inner_margin: 1in
outer_margin: 0.75in

# Chapbook (5.5 x 8.5 in, tight)
paperwidth: 5.5in
paperheight: 8.5in
inner_margin: 0.875in
outer_margin: 0.625in

# Hardcover (6 x 9 in)
paperwidth: 6in
paperheight: 9in
inner_margin: 1in
outer_margin: 0.75in

# A5 / European paperback
paperwidth: 148mm
paperheight: 210mm
inner_margin: 20mm
outer_margin: 15mm
```

IngramSpark minimum inside margins by page count:
- Under 300 pages: 0.75 in
- 300–500 pages: 0.875 in
- Over 500 pages: 1.0 in (hardcover), 0.875 in (paperback)

## Build Commands

```powershell
# Draft mode (fast — skips PDF/X pass, one LaTeX run)
.\.venv\Scripts\texgraph.exe build --project <id> --draft

# Full production build (PDF/X-3)
.\.venv\Scripts\texgraph.exe build --project <id>

# Watch mode (auto-rebuild on file save)
.\.venv\Scripts\texgraph.exe watch --project <id>
```

Output goes to `projects/<project_id>/interior/output/`.

## Draft Mode vs. Production Build

Set `draft_mode: true` in `collection.yaml` for fast iteration. This skips
the PDF/X compliance pass and runs only one LaTeX pass (no cross-references
resolved). Set `draft_mode: false` for final production output.

## Font Requirements

`mainfont` must be installed on the system as an OpenType font accessible by
LuaLaTeX. Verify font availability with:

```powershell
fc-list | Select-String "<font name>"
```

If LuaLaTeX cannot find the font, the build fails with a font-not-found error.
Use the exact name as shown by `fc-list`.

## PDF/X Compliance Checks

After a production build, verify font embedding:

```powershell
pdffonts projects/<project_id>/interior/output/<output>.pdf
```

All fonts must show `emb: yes`. Partial embedding or missing fonts fail most
vendor requirements.

## Vendor Submission Checklist

Before submitting to a print vendor (IngramSpark, KDP, BookVault, etc.):

1. Trim size matches one of the vendor's supported sizes
2. All margins meet vendor minimums for the page count
3. Bleed: none for interior; 0.125 in on cover files only
4. Color mode: B&W interior confirmed (no color declarations)
5. PDF standard: PDF/X-1a (IngramSpark) or PDF/X-3 (general)
6. All fonts fully embedded (verified with `pdffonts`)
7. Page count is even (add blank page if necessary)
8. Physical proof ordered before public listing

## Proof Pipeline (one-poem-per-page editions)

The `proof-build` command renders a fragment-per-unit tree under
`interior/output/proof/tex/` and compiles a single book PDF. It uses the
`proof_*` templates (`proof_preamble`, `proof_fragment`, `proof_master`), which
implement the omnibus page architecture:

- **One poem per page**, placement decided by the poem's *measured* height in
  TeX (the `poemblock` environment), not a Python line count. Short poems are
  centered; medium poems are top-set from a fixed sink so titles align across
  spreads; a poem just over a page is squeezed onto one page with
  `\enlargethispage`; only genuinely long poems flow across pages.
- **Stanzas never split**: the `verse` package's line break is patched to
  `\nobreak`, so a page break can fall only at an inter-stanza gap.
- **Full-page recto dividers** for in-book parts; **recto title page** per book;
  **per-volume endnotes** (`\theendnotes` between books).
- Chapter-level matter (intro, notes, afterword) uses `openany` — no forced
  rectos, so no blank versos carrying a stray folio.

Placement knobs (in `render_config`, relative to the text block so they are
trim-independent):

| Key | Default | Meaning |
|---|---|---|
| `short_poem_maxheight` | `0.62\textheight` | below this measured height, a poem is centered |
| `page_squeeze` | `3\baselineskip` | max overrun `\enlargethispage` may absorb to keep a poem whole |

Build a variant trim (hardcover/softcover) through the *same* pipeline rather
than letting style sheets drift onto the older `build` templates:

```powershell
.\.venv\Scripts\texgraph.exe proof-build --config projects/<id>/interior/collection_hardcover.yaml
```

This writes to `interior/output/proof-<name>/`, leaving the trade proof intact.

## Visual Proof Review (mandatory before sign-off)

Do not verify a typeset proof by reading the generated `.tex`. Render the key
leaves and look:

```powershell
.\.venv\Scripts\texgraph.exe proof-preview --project <id>          # structural pages
.\.venv\Scripts\texgraph.exe proof-preview --project <id> --pages 40,120 --sample 50
```

`proof-preview` detects structural pages by content (title pages, dividers, and
short centered poems are near-empty leaves) and renders them to
`interior/output/proof/preview/*.png`. A sparse page that is *not* a title or
divider is usually a defect — an orphaned closing line or a blank leaf with a
folio. Open the PNGs and confirm: book openings, every part divider, short
poems centered (not stranded at the top), long poems breaking only between
stanzas, and no blank page carrying a page number.

## Content Structure Invariant

`scan_collection` treats only the immediate subdirectories of the reading
directory as sections, and only the `.md` files *directly* inside a section are
typeset. A `.md` nested a further level down is unreachable and is now a hard
build error (it once silently dropped an entire poem sequence). Keep poems flat
within a section; front matter (`_title.md`, `00_dedication.md`) lives beside
them and is ordered ahead of the body by type, not filename.

## Guardrails

- Never alter source poem `.md` files or YAML front matter for typesetting reasons.
- `render_config` changes belong in `collection.yaml` (or a variant style sheet) only.
- Template changes require a comment explaining why the default was insufficient.
- Do not commit vendor-specific constraints as permanent spec changes without
  documenting the rationale.
- Sign off a proof only after a visual review of the rendered pages, never from
  the `.tex` alone.
