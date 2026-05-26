# Texgraph Repository Ontology

> Read this file when you need to navigate the repo structure, understand file
> formats, route a request to the correct stage, or verify system invariants.
> This is the single authoritative reference for repo shape. `AGENTS.md` is the
> dispatcher; this file is the map.

---

## Quick Routing Guide

| Request involves | Stage | Project path |
|---|---|---|
| Finding, downloading, or registering sources | `ingest/` | `projects/<id>/ingest/` |
| Transcribing text from source scans | `transcribe/` | `projects/<id>/transcribe/` |
| Auditing, correcting, or editorial prose | `proof/` | `projects/<id>/proof/` |
| Building PDFs, managing poems, setting layout | `typeset/` | `projects/<id>/typeset/` |
| Cover assets or cover production | `covers/` | `projects/<id>/covers/` |
| E-reader, web, publication-facing output | `front-end/` | `projects/<id>/front-end/` |
| Release packaging or delivery | `final/` | `projects/<id>/final/` |
| CLI, Studio, tests, infrastructure, docs | `machinery/` | `machinery/` |

---

## Directory Taxonomy

### Root-level files

| File | Purpose |
|---|---|
| `AGENTS.md` | Root dispatcher: routing table, DAG, invariants, loops |
| `ONTOLOGY.md` | This file — comprehensive repo reference |
| `PERSONA.md` | Editorial voice contract template for generative prose |
| `workspace.example.yaml` | Template for local workspace registration |
| `workspace.yaml` | Local workspace (gitignored — copy from example) |
| `pyproject.toml` | Python package definition, all dependencies |
| `requirements.txt` | Consolidated pip dependency manifest |
| `Makefile` | Build task shortcuts |

### Stage framework directories (root-level)

Each stage directory is a **framework directory**, not a project directory. It
owns contracts and reusable workflows — not project data.

```
<stage>/
  AGENTS.md              ← stage contract: inputs, outputs, gate, skills, tools
  skills/
    <skill-name>/
      SKILL.md           ← reusable workflow program, loaded on demand
  tools/
    <script>.py          ← deterministic helper scripts owned by this stage
```

Stages: `ingest/`, `transcribe/`, `proof/`, `typeset/`, `covers/`, `front-end/`,
`final/`

### machinery/

All executable code and cross-stage infrastructure.

```
machinery/
  src/
    texgraph/            ← build system: CLI, config, parser, renderer, compiler
    fletcher/            ← editorial tools: audit, metadata, PDF, archive, scan
  studio/
    backend/             ← FastAPI services (projects, builds, covers, previews)
    frontend/            ← React + Vite + TypeScript Studio interface
  tests/                 ← regression test suite
  docs/                  ← technical reference documents
  skills/                ← cross-stage infrastructure workflow programs
  tools/                 ← cross-stage infrastructure scripts
```

### projects/

Local project workspaces. Gitignored except tracked example projects.

```
projects/
  <project_id>/
    ingest/
      raw/               ← renamed source files (<stable_name>.<ext>)
                            provenance records (<stable_name>.provenance.yaml)
      PROMOTION.yaml     ← stage gate: sources approved for transcription
    transcribe/
      PROMOTION.yaml     ← stage gate: volumes transcribed and policy accepted
      <volume files, plans, metadata>
    proof/
      PROMOTION.yaml     ← stage gate: corrections complete, proof PDF present
      <audit reports, corrections>
    typeset/             ← collection.yaml, content/, output/ (build root)
      PROMOTION.yaml     ← stage gate: interior PDF embedded and approved
    covers/
      PROMOTION.yaml     ← stage gate: final PDF present, cover unlock set
      <cover assets and production files>
    front-end/           ← publication-facing assets
    final/               ← release packages, manifests

  spectra_poems/         ← tracked example project (in git)
```

Build roots point at `projects/<project_id>/typeset/`. The `workspace.yaml` file
registers each project ID and its typeset path.

---

## File Type Glossary

| File / Pattern | Meaning |
|---|---|
| `AGENTS.md` | Stage contract or root dispatcher. Read first when entering a stage. |
| `SKILL.md` | Reusable workflow program. Load on demand when the task matches. |
| `ONTOLOGY.md` | Comprehensive repo reference (this file). |
| `PERSONA.md` | Editorial voice contract. Load only for generative/voice-led work. |
| `collection.yaml` | Project metadata and render_config. The build root's single config. |
| `workspace.yaml` | Maps project IDs to typeset paths. Local, gitignored. |
| `workspace.example.yaml` | Template for workspace.yaml. In git. |
| `_meta.yaml` | Section metadata in a content directory (label, order, type). |
| `*.md` in `content/` | Poem or prose file with YAML front matter. |
| `*.tex.jinja2` | LaTeX document template rendered by the build system. |
| `*.xmp.jinja2` | PDF/X XMP metadata template. |
| `book.json` | Per-book derived metadata. Generated by `texgraph metadata`. |
| `book.md` | Volume/book manifest with YAML front matter. |
| `volume.md` | Volume-level manifest with YAML front matter. |
| `.ontology-baseline` | Stored git hash for ontology_check.py comparisons. Gitignored. |
| `PROMOTION.yaml` | Stage gate record at `projects/<id>/<stage>/PROMOTION.yaml`. Written by `texgraph ingest rename` / `texgraph promote`. Read by `texgraph verify`. |
| `<stable_name>.provenance.yaml` | Source provenance record beside the renamed ingest file. Documents origin, rights, SHA-256 checksum, ingested_at timestamp, and notes. |

---

## Data Schemas

### collection.yaml

```yaml
title: "Collection Title"
subtitle: "Optional Subtitle"           # omit if none
author: "Author Name"
year: 2026
publisher: "Publisher Name"
isbn: ""                                 # empty until assigned
language: en
content_dir: content                     # relative to this file
output_dir: output                       # relative to this file
lualatex_path: lualatex                  # PATH name or absolute path
draft_mode: false                        # true = skip PDF/X, one LaTeX run

render_config:
  fontsize: 11pt                         # 10pt | 11pt | 12pt
  mainfont: EB Garamond                  # OpenType font name; must be installed
  paperwidth: 5.5in                      # page width (in, mm, cm, pt)
  paperheight: 8.5in                     # page height
  top_margin: 1in
  bottom_margin: 1in
  inner_margin: 1in                      # gutter margin
  outer_margin: 0.75in
  line_spread: 1.1                       # leading multiplier
  stanza_skip: 1.2ex                     # vertical space between stanzas
```

### Poem Markdown front matter

```yaml
---
title: "Poem Title"
type: poem                               # poem | prose | poem-cycle | poem-screenplay
order: 1                                 # integer, controls sequence within section
subtitle: ""                             # optional
epigraph: ""                             # optional
dedication: ""                           # optional
---

First line of poem body.
```

Stanzas are separated by blank lines. Leading spaces are preserved as
indentation in the rendered verse environment.

### Section _meta.yaml

```yaml
id: section-slug                         # informational; canonical id is directory name
type: section
label: "Display Label"
order: 1                                 # controls section sequence in the build
```

### workspace.yaml

```yaml
projects:
  - id: project-slug                     # used with --project flag
    path: projects/project-slug/typeset  # relative to workspace.yaml
    description: "Human description"
default_project: project-slug
```

### Stable source naming schema

Renamed ingest files follow this pattern:

```
<author_slug>_<year>_<title_slug>_<source_slug>.<ext>
```

- `author_slug` — hyphen-separated lowercase author last name(s), e.g. `keats`
- `year` — four-digit publication year, e.g. `1820`
- `title_slug` — hyphen-separated lowercase title words, e.g. `lamia-and-other-poems`
- `source_slug` — `upload` (default) or descriptive slug for the source origin
- `ext` — original file extension preserved (`.pdf`, `.docx`, `.txt`, etc.)

Example: `keats_1820_lamia-and-other-poems_upload.pdf`

The presence of a stable-named file certifies it has been processed through ingest. The original file is gone after rename — moving, not copying, is the intentional design: the rename is the record of processing.

### PROMOTION.yaml — ingest stage

Written by `texgraph ingest rename`; approved manually via `texgraph promote ingest`.

```yaml
status: pending                    # pending | approved
sources:
  - stable_name: keats_1820_lamia-and-other-poems_upload.pdf
    stable_path: ingest/raw/keats_1820_lamia-and-other-poems_upload.pdf
    original_name: Lamia 1820.pdf
    source_type: upload            # upload | internet_archive | scan | other
    rights: unknown                # unknown | public_domain | licensed | restricted
    access_confirmed: true
    checksum_sha256: "abc123..."
    ingested_at: "2026-05-26T14:00:00"
    page_count: 120                # optional
    notes: ""
```

Gate condition for `transcribe`: `status == approved` and all sources have `access_confirmed: true` with `stable_path` present on disk.

### PROMOTION.yaml — transcribe stage

```yaml
status: pending                    # pending | approved
policy_accepted: true
all_statuses_at_least: transcribed # transcribed | checked | final
uncertain_readings_accepted: false # true = user has explicitly accepted open readings
volumes:
  - id: vol-1
    transcription_status: transcribed  # not_started | transcribed | checked | final
    uncertain_readings: []             # list of unresolved reading notes
```

Gate condition for `proof`: `status == approved`, `policy_accepted`, all volumes meet `all_statuses_at_least` floor, and `uncertain_readings_accepted` if any open readings exist.

### PROMOTION.yaml — proof stage

```yaml
status: pending                    # pending | approved
proof_pdf: proof/output/proof.pdf  # path relative to project root
textual_questions:
  open: 0                          # must be 0 for promotion
  resolved: 12
page_count: 128                    # must be even for print
user_accepted_layout: true
```

Gate condition for `typeset`: `status == approved`, `proof_pdf` exists on disk, `textual_questions.open == 0`, `page_count` is even, `user_accepted_layout`.

### PROMOTION.yaml — typeset stage

```yaml
status: pending                    # pending | approved
interior_pdf: typeset/output/my-collection.pdf
fonts_embedded: true               # verified with pdffonts
user_approved_interior: true
```

Gate condition for `covers`: `status == approved`, `interior_pdf` exists on disk, `fonts_embedded`, `user_approved_interior`.

### PROMOTION.yaml — final stage

```yaml
status: pending                    # pending | approved
final_pdf: final/output/my-collection-final.pdf
cover_unlock:
  unlocked: true
  unlocked_at: "2026-05-26T14:00:00"
```

Gate condition for `covers`: `status == approved`, `final_pdf` exists on disk, `cover_unlock.unlocked`.

### Book manifest front matter (transcription projects)

```yaml
---
title: "Book Title"
book_order: 1
author: "Author Name"
publisher: "Publisher"
place: "City"
year: 1913
source_pdf: "ingest/raw/<stable>.pdf"
source_status: present                   # present | missing | working_source_reprint | access_restricted | pending_acquisition
pdf_pages: 120
transcription_status: in_progress        # not_started | in_progress | transcribed | checked | final
notes: ""
---
```

### Source matter file front matter

```yaml
---
title: "Dedication"
book: "Book Title"
book_order: 1
matter_order: 1
matter_section: front                    # front | back
matter_type: dedication                  # dedication | preface | contents | epigraph |
                                         # acknowledgment | illustration_list |
                                         # frontispiece | dedicatory_poem |
                                         # colophon | publisher_ad | appendix
source_pdf: "ingest/raw/<stable>.pdf"
source_pages_scan: "1-2"
source_pages_printed: "i-ii"
status: transcribed
notes: ""
---
```

---

## Pipeline Architecture

```
project-create
      │
      ▼
   ingest            source files, provenance, page counts
      │  ── user gate: source set + naming approved ──
      ▼
 transcribe          poem text, source matter, volume plans, metadata
      │  ── user gate: policy + uncertain readings resolved ──
      ▼
   proof             audits, corrections, editorial review
      │  ── user gate: corrections + proof status approved ──
      ├──────────────────────────────────────────────────────┐
      ▼                                                      ▼
  typeset            layout, PDF builds              (direct-to-final
      ├────────────────────────┐                      for short-form)
      ▼                        ▼
   covers                 front-end         e-reader, web, publication
      │                        │
      └──────────┬─────────────┘
                 │  ── user gate: final signoff ──
                 ▼
              final            release packages, manifests, delivery
```

### Stage ownership rules

- Each stage **owns its artifacts**. It does not write to another stage's
  directory without explicit user approval.
- Stages read from upstream artifacts; they never modify them.
- Promotion gates are always explicit. Silent cross-stage edits are forbidden.
- `final/` receives only user-approved artifacts from upstream.

### Content type routing within stages

When the task involves specific content types, load the matching sub-skill:

| Content type | Transcribe skill | Proof skill | Typeset skill |
|---|---|---|---|
| Verse (lyric, formal, free) | `poem-transcription` | `poetry-proof` | `poetry` |
| Prose (preface, essay, fiction) | `prose-transcription` | `prose-proof` | `prose` |
| Source paratext | `source-matter` | `transcription-verification` | `prose` |
| Documentation / repo structure | — | — | `technical-docs` (machinery) |

---

## Command Surface

Both `texgraph` and `fletcher` invoke the same CLI. `fletcher` is an alias.

### Build and workspace commands

| Command | Stage | What it does |
|---|---|---|
| `texgraph build [--project <id>] [--draft]` | typeset | Parse → render → compile PDF |
| `texgraph watch [--project <id>]` | typeset | Auto-rebuild on file changes |
| `texgraph list` | workspace | List registered projects |
| `texgraph new poem "Title" [--section <id>]` | typeset | Scaffold poem file |
| `texgraph studio` | machinery | Launch FastAPI + React Studio |

### Pipeline gate commands

| Command | Stage | What it does |
|---|---|---|
| `texgraph verify <stage> [--project <id>]` | all | Check upstream PROMOTION.yaml preconditions; exits 0 on pass, 1 on fail |
| `texgraph ingest rename <file> --author A --year Y --title T [--source S] [--project <id>]` | ingest | Rename source to stable name, write provenance record, update ingest PROMOTION.yaml |

### Editorial and source commands

| Command | Stage | What it does |
|---|---|---|
| `texgraph pdf info <pdf> [--json]` | ingest | Metadata via pdfinfo |
| `texgraph pdf text <pdf> --first N --last N` | ingest | Extract text via pdftotext |
| `texgraph pdf render <pdf> --first N --last N --prefix P` | ingest | Pages to PNG |
| `texgraph archive files <identifier>` | ingest | List Internet Archive files |
| `texgraph archive download <id> <file> <dest>` | ingest | Download from IA |
| `texgraph audit <volume> [--json]` | proof | Audit transcription book dir |
| `texgraph metadata <target> [--write] [--check]` | transcribe | book.json metadata |
| `texgraph page-map --offset N --printed "<ranges>"` | transcribe | Page number mapping |
| `texgraph plan <document> [--check]` | transcribe | Plan heading structure |
| `texgraph scan <target> --output <path>` | transcribe | PDF front/back matter scan |

### Studio API (default: http://localhost:8765)

| Route | Purpose |
|---|---|
| `GET /api/projects` | List workspace projects |
| `POST /api/projects` | Create a project |
| `GET /api/projects/{id}/sections/{sid}/poems` | List poems in section |
| `POST /api/projects/{id}/build` | Trigger build |
| `GET /api/projects/{id}/preview` | Generate preview |
| `POST /api/agent` | Agent endpoints |
| `GET/POST /api/covers` | Cover management |
| `GET /health` | Health check |

---

## Dependency Map

### Python packages (core — pyproject.toml)

| Package | Used by | Purpose |
|---|---|---|
| `python-frontmatter` | parser.py | YAML front matter parsing from .md files |
| `jinja2` | renderer.py | LaTeX template rendering |
| `pyyaml` | config.py, models.py | YAML config and manifest parsing |
| `typer` | cli.py | CLI framework |
| `rich` | cli.py | Terminal output formatting |
| `watchdog` | cli.py (watch) | File system event monitoring |
| `python-dotenv` | config.py | .env file loading |
| `pydantic` | fletcher/models.py, studio | Data validation |
| `mistune` | (available, not active) | Markdown parsing |

### Python packages (studio — requirements-studio.txt)

| Package | Used by | Purpose |
|---|---|---|
| `fastapi` | studio/backend | Web framework |
| `uvicorn[standard]` | studio/backend | ASGI server |
| `pydantic-settings` | studio/backend/core/config.py | Settings management |
| `aiofiles` | studio/backend | Async file I/O |
| `python-multipart` | studio/backend | Form/file upload handling |
| `watchfiles` | studio/backend | File watching for live reload |
| `anthropic` | studio/backend/services/agent_service.py | Claude API for agent service |

### External binaries (ingest tools, optional)

| Binary | Package | Purpose |
|---|---|---|
| `pdfinfo` | poppler-utils | PDF metadata extraction |
| `pdftotext` | poppler-utils | PDF text extraction |
| `pdftoppm` | poppler-utils | PDF page rendering to PNG |
| `lualatex` | TeX Live / MiKTeX | LaTeX compilation |
| `pdffonts` | poppler-utils | Font embedding verification |

---

## Key Invariants

These must always be true. Violating any of them breaks the system.

1. **`section_id` is the directory name**, not `_meta.yaml:id`. The build system
   uses the directory name as the canonical section identifier.

2. **Shared Python helpers belong in `machinery/src/texgraph/utils.py`**. Do not
   place shared logic in `cli.py` or other modules.

3. **Studio backend resolves project paths through workspace/project services**,
   not by constructing paths directly.

4. **Version sidecars use `.slug.versions.yaml`**. Canonical selection must match
   build behavior exactly.

5. **Persona prose never enters source text, YAML, manifests, audits, or command
   output**. The edition can have a house voice; the transcription cannot.

6. **Stage isolation**: a stage agent writes only to `projects/<id>/<stage>/`.
   Cross-stage writes require explicit user approval.

7. **Promotion gates are explicit**. User approval at each DAG edge is not
   optional and not automated.

8. **External knowledge must be cited** when it affects source facts, rights,
   editorial decisions, or production choices. It never overrides source evidence
   silently.

9. **`.env` is never committed**. It is gitignored and contains live credentials.

10. **`projects/` is gitignored** except explicitly tracked example projects
    listed in `.gitignore` as negation rules (e.g., `!projects/spectra_poems/`).

11. **`texgraph` and `fletcher` are aliases for the same CLI**. Keep command
    names stable; treat both as compatibility entrypoints.

12. **`PROMOTION.yaml` is the machine-readable gate**. A stage does not begin
    work unless the upstream PROMOTION.yaml exists and passes `texgraph verify`.
    The file lives at `projects/<id>/<stage>/PROMOTION.yaml`. Writing `status:
    approved` requires explicit user action via `texgraph promote <stage>` (not
    yet implemented — stages 4–7 of the gate implementation plan).

13. **Stable source naming is the ingest certification**. A file named according
    to the schema `<author>_<year>_<title>_<source>.<ext>` in `ingest/raw/`
    certifies it has been processed. The original file is gone — `texgraph ingest
    rename` moves, not copies. Presence of the renamed file is the processing record.

---

## Installation and Setup

### First-time install

```powershell
# Create venv and install all dependencies
python -m venv .venv
.\.venv\Scripts\pip.exe install -e .
.\.venv\Scripts\pip.exe install -r machinery\studio\requirements-studio.txt

# Copy workspace template
Copy-Item workspace.example.yaml workspace.yaml
# Edit workspace.yaml to register your project(s)
```

### Run the example project

```powershell
# Build the tracked spectra_poems example (draft mode — fast)
.\.venv\Scripts\texgraph.exe build --project spectra_poems --draft
```

### Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest machinery\tests -q
```

---

## Update Protocol

Update this file when any of the following change:

- **Directory structure**: new stages, renamed directories, new project layout
- **File type conventions**: new extensions, new naming patterns
- **Data schemas**: new fields, changed field names, new file types
- **Command surface**: new commands, renamed flags, removed commands
- **Key invariants**: new must-be-true facts, removed constraints
- **Pipeline architecture**: new stages, changed DAG edges
- **Dependency map**: new packages, removed packages, new external binaries

After any significant task, run the ontology checker:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

If it flags changes in tracked areas, update the relevant sections here, then
save a new baseline:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```
