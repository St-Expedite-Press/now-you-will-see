# Interior Module Runbook

Operator guide for proof draft and production PDF builds. See `AGENTS.md` for
the module contract. See `machinery/docs/ONTOLOGY.md § Data Schemas` for
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

## Proof build (first-draft review PDF)

A proof build is a single LuaLaTeX pass — no PDF/X compliance, faster output.
Use it to review layout and catch rendering issues before committing to a
production build.

```powershell
.\.venv\Scripts\texgraph.exe proof-build --project <id>
```

Output lands at `projects/<id>/interior/output/proof/` (or
`projects/<id>/typeset/output/proof/` for unmigrated projects).

### Expected outputs

| File | Description |
|---|---|
| `output/proof/<collection>.tex` | Rendered LuaLaTeX source |
| `output/proof/<collection>.pdf` | Draft PDF (single pass, no PDF/X) |

### Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `collection.yaml not found` | Wrong project ID or unmigrated workspace path | Run `texgraph list` to check registered paths |
| `lualatex not found` | LuaLaTeX not on PATH | Install TeX Live or MiKTeX and add `lualatex` to PATH |
| Missing font | Font name in `collection.yaml:render_config.mainfont` not installed | Install the font system-wide |
| Blank PDF / render error | Section `_meta.yaml` missing required fields | Run `texgraph audit <volume>` |

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
