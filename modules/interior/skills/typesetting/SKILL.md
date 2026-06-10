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
`typeset/skills/poetry/SKILL.md`. For prose layout, load
`typeset/skills/prose/SKILL.md`.

## Required Reads

- `projects/<project_id>/typeset/collection.yaml` — current render_config
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

Output goes to `projects/<project_id>/typeset/output/`.

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
pdffonts projects/<project_id>/typeset/output/<output>.pdf
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

## Guardrails

- Never alter source poem `.md` files or YAML front matter for typesetting reasons.
- `render_config` changes belong in `collection.yaml` only.
- Template changes require a comment explaining why the default was insufficient.
- Do not commit vendor-specific constraints as permanent spec changes without
  documenting the rationale.
