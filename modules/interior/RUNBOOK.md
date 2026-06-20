# Interior Module Runbook

Operator guide for proof draft and production PDF builds. See `AGENTS.md` for
the module contract. See `README.md § Data Schemas` for
`collection.yaml` and `PROMOTION.yaml` field reference.

---

## Prerequisites

Before starting interior work, the upstream transcription gate must pass:

```powershell
.\.venv\Scripts\texgraph.exe verify interior --project <id>
```

Expected output: `OK  transcription/PROMOTION.yaml passes all preconditions.`

If it fails, resolve the issues reported (transcription PROMOTION.yaml missing or
`status != approved`) before proceeding.

---

## Proof build (review PDF — the omnibus pipeline)

`proof-build` is the full interior pipeline (the `proof_*` templates): a
fragment per content unit, one-poem-per-page placement decided by measured
height, full-page recto part dividers, per-book recto title pages, and keyed
back-matter notes. Two LuaLaTeX passes resolve the TOC and page references.

```powershell
# Trade review proof (collection.yaml)
.\.venv\Scripts\texgraph.exe proof-build --project <id>

# A variant style sheet (hardcover / softcover) through the SAME pipeline —
# writes to output/proof-<name>/ so it never clobbers the trade proof
.\.venv\Scripts\texgraph.exe proof-build --config projects/<id>/interior/collection_hardcover.yaml
```

Output lands at `projects/<id>/interior/output/proof/` (variants:
`output/proof-<name>/`). See `modules/interior/skills/typesetting/SKILL.md` for
the page-mode (`one-per-page` vs `flow`) and placement knobs.

### Visual review (mandatory before sign-off)

Never sign off layout from the generated `.tex`. Render the structural pages and look:

```powershell
.\.venv\Scripts\texgraph.exe proof-preview --project <id>          # title pages, dividers, sparse leaves
.\.venv\Scripts\texgraph.exe proof-preview --project <id> --pages 40,120 --sample 50
```

Outputs PNGs to `output/proof/preview/`. Requires poppler (`pdftoppm`, `pdftotext`).
A sparse page that is not a title/divider is usually a defect (orphaned line,
stray-folio blank).

### Print-ready PDF/X (vendor upload)

For an IngramSpark-uploadable interior, add `--print-ready`: loads `pdfx`
(PDF/X-3), pads to an even page count, and writes to `output/print/<format>/`.

```powershell
.\.venv\Scripts\texgraph.exe proof-build --print-ready --config projects/<id>/interior/collection_hardcover.yaml
.\.venv\Scripts\texgraph.exe proof-build --print-ready --config projects/<id>/interior/collection_softcover.yaml
```

Verify: `pdffonts` (all `emb yes`), `pdfinfo` (even page count, correct trim,
PDF/X marker). For the omnibus editions this is the production path — not the
legacy `build` command below, which uses the older non-poetry templates.

### Expected outputs

| File | Description |
|---|---|
| `output/proof/tex/<collection>.tex` | Master + per-fragment LuaLaTeX source |
| `output/proof/<collection>.pdf` | Review PDF (2 passes) |
| `output/print/<format>/<collection>.pdf` | PDF/X-3, even pages (with `--print-ready`) |

### Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `markdown file(s) … silently dropped` | A poem nested below the section level | Flatten it into its section directory (content is flat within a section) |
| `collection.yaml not found` | Wrong project ID or unmigrated workspace path | Run `texgraph list` to check registered paths |
| `lualatex not found` | LuaLaTeX not on PATH | Install TeX Live or MiKTeX and add `lualatex` to PATH |
| Missing font | `render_config.mainfont` not installed | Install the font system-wide |
| PDF emitted as US Letter | `pdfx` loaded before geometry | Already handled in the proof preamble; keep `pdfx` after geometry |

---

## Production build (interior PDF)

Runs three LuaLaTeX passes and generates PDF/X-compliant XMP metadata.

```powershell
.\.venv\Scripts\texgraph.exe build --project <id>
```

Or in draft mode (fast, skips PDF/X):

```powershell
.\.venv\Scripts\texgraph.exe build --project <id> --draft
```

Output lands at `projects/<id>/interior/output/`.

### Verify font embedding after build

```powershell
pdffonts projects/<id>/interior/output/<collection>.pdf
```

All fonts should show `yes` in the `emb` column. If any show `no`, the
production build is not print-ready.

---

## Continuous watch mode

During active editing, the watcher rebuilds on every file change:

```powershell
.\.venv\Scripts\texgraph.exe watch --project <id>
```

Watch mode runs in draft mode by default (one pass, fast). Stop with Ctrl-C.

---

## Promote interior

After the interior PDF is approved:

1. Confirm the PDF exists at `interior/output/<collection>.pdf`.
2. Confirm fonts are embedded (`pdffonts`).
3. Create or update `projects/<id>/interior/PROMOTION.yaml`:

```yaml
status: pending
interior_pdf: interior/output/<collection>.pdf
fonts_embedded: true
user_approved_interior: true
```

4. Run promote:

```powershell
.\.venv\Scripts\texgraph.exe promote interior --project <id>
```

This sets `status: approved` and unlocks the `covers`, `publication`, and
`release` downstream modules.

Verify the promotion took effect:

```powershell
.\.venv\Scripts\texgraph.exe verify covers --project <id>
```

---

## Render configuration reference

`collection.yaml:render_config` controls layout. Key fields:

| Field | Default | Notes |
|---|---|---|
| `fontsize` | `11pt` | `10pt`, `11pt`, or `12pt` |
| `mainfont` | `EB Garamond` | Must be installed as an OpenType font |
| `paperwidth` | `5.5in` | Use `in`, `mm`, `cm`, or `pt` |
| `paperheight` | `8.5in` | |
| `top_margin` | `1in` | |
| `bottom_margin` | `1in` | |
| `inner_margin` | `1in` | Gutter side |
| `outer_margin` | `0.75in` | |
| `line_spread` | `1.1` | Leading multiplier |
| `stanza_skip` | `1.2ex` | Vertical space between stanzas |

Skills for poetry, prose, and general typesetting live under
`modules/interior/skills/`.
