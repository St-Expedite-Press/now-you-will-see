# Quick Start

A linear path from a clean install to your first built PDF. Takes 15–30 minutes
depending on how quickly TeX Live installs.

---

## Prerequisites

Before installing Texgraph, you need:

| Requirement | Version | Purpose | Install |
|---|---|---|---|
| Python | 3.11 or later | Runtime | [python.org](https://www.python.org/downloads/) |
| TeX Live or MiKTeX | Full install | LuaLaTeX compiler | [tug.org/texlive](https://tug.org/texlive/) / [miktex.org](https://miktex.org/) |
| OpenType font | Any | Body type for your collection | See below |
| poppler-utils | Any | PDF inspection for ingest/transcription | Optional — see below |
| Node.js | 18+ | Studio frontend only | Optional — see below |

**TeX Live note:** Install the full scheme, not the minimal scheme. The full
install (~4 GB) includes all packages Texgraph needs. With a minimal install,
the build will fail with missing package errors. On Windows, MiKTeX with
auto-install enabled is an acceptable alternative.

**Font note:** The example project uses EB Garamond. Install it as a system
font so LuaLaTeX can find it. On Windows: download from
[fonts.google.com/specimen/EB+Garamond](https://fonts.google.com/specimen/EB+Garamond),
right-click the `.ttf` files → Install for all users.

**poppler-utils:** Required only for `texgraph pdf`, `texgraph archive`,
`texgraph audit`, and `texgraph scan`. Not needed for build/watch/list.
On Windows, get it from [poppler.freedesktop.org](https://poppler.freedesktop.org/)
or via Conda: `conda install -c conda-forge poppler`.

**Node.js:** Required only if you are running the Studio frontend from source.
Not required for CLI builds.

---

## 1. Install

```powershell
# Clone the repo
git clone https://github.com/St-Expedite-Press/now-you-will-see.git texgraph
cd texgraph

# Create venv and install the package
python -m venv .venv
.\.venv\Scripts\pip.exe install -e .

# Verify the CLI is available
.\.venv\Scripts\texgraph.exe --help
```

You should see the Texgraph help output listing all commands. If you get a
`command not found` or import error, check that `.venv` was created from
Python 3.11+.

---

## 2. Verify TeX and fonts

```powershell
# Check lualatex is on your PATH
lualatex --version

# Check the font is findable
fc-list | findstr "EB Garamond"
```

`fc-list` is part of fontconfig. On Windows you may need to run it through WSL
or use the MiKTeX console to verify fonts. If EB Garamond does not appear, the
build will fail with a font-not-found error.

---

## 3. Register the example project

```powershell
Copy-Item workspace.example.yaml workspace.yaml
```

Open `workspace.yaml` and confirm it lists `spectra_poems`:

```yaml
projects:
  - id: spectra_poems
    path: projects/spectra_poems/typeset
    description: "Iberian Dreams — tracked example"
default_project: spectra_poems
```

```powershell
# Confirm it's registered
.\.venv\Scripts\texgraph.exe list
```

---

## 4. Build the example project

```powershell
# Draft build — fast, skips PDF/X compliance pass
.\.venv\Scripts\texgraph.exe build --project spectra_poems --draft
```

A successful build prints something like:

```
Building spectra_poems (draft mode)...
  Parsed 3 poems across 1 section
  Rendered LaTeX: output/spectra_poems.tex
  Compiled: output/spectra_poems.pdf
Done.
```

The output PDF is at:

```
projects/spectra_poems/typeset/output/
```

Open it. You should see three poems ("In Response, A Sonnet", "No Serrana",
"The Marques Dreams of Her") typeset in EB Garamond at 5.5×8.5 inches.

---

## 4a. Optional: Run Studio and the audit dashboard

Studio is the local React/FastAPI interface. It is not required for CLI builds.
Use `machinery/docs/STUDIO_FRONTEND.md` for the Studio frontend setup, route
checks, and audit dashboard smoke tests.

---

## 5. Add your own poem

```powershell
# Scaffold a new poem in the existing section
.\.venv\Scripts\texgraph.exe new poem "My Poem Title" --section iberian-dreams
```

This creates a new `.md` file in
`projects/spectra_poems/typeset/content/01_iberian-dreams/` with standard
front matter. Open it and fill in the body text.

Rebuild to see the result:

```powershell
.\.venv\Scripts\texgraph.exe build --project spectra_poems --draft
```

Or use watch mode to rebuild automatically on every save:

```powershell
.\.venv\Scripts\texgraph.exe watch --project spectra_poems
```

---

## 6. Start your own project

Create the project directory structure:

```powershell
New-Item -ItemType Directory -Path projects\my-collection\typeset\content\01_poems -Force
```

Create `projects/my-collection/typeset/collection.yaml`:

```yaml
title: "My Collection"
subtitle: ""
author: "Your Name"
year: 2026
publisher: ""
isbn: ""
language: en
content_dir: content
output_dir: output
lualatex_path: lualatex
draft_mode: false

render_config:
  fontsize: 11pt
  mainfont: EB Garamond
  paperwidth: 5.5in
  paperheight: 8.5in
  top_margin: 1in
  bottom_margin: 1in
  inner_margin: 0.875in
  outer_margin: 0.75in
  line_spread: 1.1
  stanza_skip: 1.2ex
```

Create `projects/my-collection/typeset/content/01_poems/_meta.yaml`:

```yaml
id: poems
type: section
label: "Poems"
order: 1
```

Register it in `workspace.yaml`:

```yaml
projects:
  - id: spectra_poems
    path: projects/spectra_poems/typeset
    description: "Tracked example"
  - id: my-collection
    path: projects/my-collection/typeset
    description: "My collection"
default_project: my-collection
```

Add a poem and build:

```powershell
.\.venv\Scripts\texgraph.exe new poem "First Poem" --section poems
.\.venv\Scripts\texgraph.exe build --project my-collection --draft
```

---

## 7. Production build

When you are ready for a print-vendor-ready file, turn off draft mode in
`collection.yaml` (`draft_mode: false`) and run a full build:

```powershell
.\.venv\Scripts\texgraph.exe build --project my-collection
```

This produces a PDF/X-3 file with embedded fonts and XMP metadata. Verify
font embedding before submitting to a vendor:

```powershell
pdffonts projects\my-collection\typeset\output\my-collection.pdf
```

All fonts should show `emb: yes`. If any do not, the vendor will reject the file.

---

## Common Errors

**`lualatex not found`**
TeX Live is not on your PATH. On Windows, run the TeX Live installer and ensure
it adds itself to `%PATH%`, or use the MiKTeX installer.

**`Font "EB Garamond" not found`**
The font is not installed as a system font. Download and install it, then rebuild.

**`Missing package: <name>`**
Your TeX installation is missing a required package. With TeX Live full scheme
this should not occur. With MiKTeX, enable auto-install or run the MiKTeX package
manager and install the package manually.

**`FileNotFoundError` or import error on `.\.venv\Scripts\texgraph.exe`**
The package was not installed into the venv. Run `.\.venv\Scripts\pip.exe install -e .` again.

---

## Next Steps

- `ONTOLOGY.md` — comprehensive reference for directory structure, all file schemas, command surface, key invariants
- `AGENTS.md` — how to classify and route tasks through the pipeline with AI assistance
- `machinery/docs/STUDIO_FRONTEND.md` — Studio frontend setup, routes, and smoke tests
- `machinery/docs/DAG_PIPELINE.md` — full pipeline graph with node contracts and gate commands
- `typeset/skills/poetry/SKILL.md` — verse-specific layout decisions
- `typeset/skills/prose/SKILL.md` — prose layout decisions
- `machinery/docs/PROCEDURES.md` — verification and workflow procedures

### Pipeline gate commands

Once you have a project and want to carry it through the full pipeline:

```powershell
# Rename an ingested source to its stable name and register it
.\.venv\Scripts\texgraph.exe ingest rename <file> --author "keats" --year 1820 --title "lamia-and-other-poems" --project my-collection

# Check that the upstream stage is ready before starting the next stage
.\.venv\Scripts\texgraph.exe verify transcribe --project my-collection
.\.venv\Scripts\texgraph.exe verify proof --project my-collection
.\.venv\Scripts\texgraph.exe verify typeset --project my-collection
.\.venv\Scripts\texgraph.exe verify final --project my-collection
```

`texgraph verify` exits 0 when the upstream gate is clear and 1 with a list of
blocking issues when it is not. Each stage writes a `PROMOTION.yaml` file when
the user approves it; downstream stages check this file before starting work.
