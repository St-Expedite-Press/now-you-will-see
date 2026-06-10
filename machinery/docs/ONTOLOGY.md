# Texgraph Repository Ontology

> Read this file when you need to navigate the repo structure, understand file
> formats, route a request to the correct module, or verify system invariants.
> This is the single authoritative reference for repo shape. `AGENTS.md` is the
> dispatcher; this file is the map.

---

## Quick Routing Guide

| Request involves | Module | Project path |
|---|---|---|
| Workspace registration and project creation | `workspace` | `workspace.yaml`, `projects/<id>/` |
| Finding, downloading, or registering sources | `sources` | `projects/<id>/sources/` |
| Transcribing text from source scans | `transcription` | `projects/<id>/transcription/` |
| Auditing, correcting, or textual review | `manuscript` | `projects/<id>/manuscript/` |
| Proof-draft rendering, layout, and interior PDFs | `interior` | `projects/<id>/interior/` |
| Legacy proof records and reusable proof skills | `proof/` legacy support | `projects/<id>/proof/` |
| Cover assets or cover production | `covers/` | `projects/<id>/covers/` |
| E-reader, web, publication-facing output | `publication` | `projects/<id>/publication/` |
| Release packaging or delivery | `release` | `projects/<id>/release/` |
| CLI, Studio, tests, infrastructure, docs | `machinery/` | `machinery/` |

---

## Job Classification

Every request has a job type before it has a module. Classify first, then route.

### Classification tree

```
Job
├── pipeline/                   ← artifact-producing, gate-gated
│   ├── sources                 → PROMOTION.yaml + sources/raw/
│   ├── transcription           → PROMOTION.yaml + transcription files
│   ├── manuscript              → corrected manuscript + proof drafts
│   ├── interior                → PROMOTION.yaml + interior PDF
│   ├── covers                  → cover files
│   ├── publication             → publication files
│   └── release                 → release package
└── non-pipeline/               ← no gate, lighter or no artifact
    ├── conversation            → no artifact (answer, decision, or plan)
    ├── research                → research note (candidate sources, rights) → feeds sources
    └── tooling                 → code/doc change (routes to machinery/)
```

### Artifact contracts

| Node | Output artifact | Written to | Downstream consumer |
|---|---|---|---|
| `pipeline/sources` | PROMOTION.yaml + raw sources | `projects/<id>/sources/` | transcription |
| `pipeline/transcription` | PROMOTION.yaml + transcription files | `projects/<id>/transcription/` | manuscript |
| `pipeline/manuscript` | corrected manuscript, corrections, textual review | `projects/<id>/manuscript/` | interior |
| `pipeline/interior` | PROMOTION.yaml + proof drafts + interior PDF | `projects/<id>/interior/` | covers / publication / release |
| `pipeline/covers` | Cover files | `projects/<id>/covers/` | release |
| `pipeline/publication` | Publication files | `projects/<id>/publication/` | release |
| `pipeline/release` | Release package | `projects/<id>/release/` | — |
| `research` | `<topic>.research.md` note (optional) | `projects/<id>/sources/` | pipeline/sources |
| `conversation` | None | — | — |
| `tooling` | Code or doc change | `machinery/` or repo root | — |

### Composite paths

| Path | When | Transition trigger |
|---|---|---|
| `pipeline/<module>` | All inputs known — rote execution | — |
| `conversation → pipeline/<module>` | Required inputs missing or ambiguous | User provides missing input |
| `research → pipeline/sources` | Source not yet identified | User approves candidate |
| `research → conversation` | Research raises an unanswerable question | Question surfaced to user |
| `conversation` | Planning, scoping, feedback — no execution | — |
| `tooling` | Framework change only | User approves scope |
| `tooling → pipeline/<module>` | Fix a tool, then use it in the same session | Tool change complete + user confirms |

### Rote vs. conversation-required

A pipeline task is **rote** when all required inputs are present (project ID, module, content type, scope). Execute immediately.

A pipeline task **requires conversation** when inputs are missing or a decision must be made before execution. Ask first, collect inputs, then re-classify and execute.

This is a property of the task instance, not the job type. For the full classifier decision tree, see `machinery/skills/task-classifier/SKILL.md`.

---

## Directory Taxonomy

### Root-level files

| File | Purpose |
|---|---|
| `AGENTS.md` | Root dispatcher: routing table, DAG, invariants, loops |
| `README.md` | Root compatibility pointer to `machinery/docs/README.md` |
| `CLAUDE.md` | Root compatibility pointer to `machinery/docs/CLAUDE.md` |
| `HANDOFF.md` | Root compatibility pointer to `machinery/docs/HANDOFF.md` |
| `ONTOLOGY.md` | Root compatibility pointer to this canonical file |
| `PERSONA.md` | Root compatibility pointer to `machinery/docs/PERSONA.md` |
| `workspace.example.yaml` | Template for local workspace registration |
| `workspace.yaml` | Local workspace (gitignored — copy from example) |
| `pyproject.toml` | Python package definition, dependencies, and package README path (`machinery/docs/PROJECT_OVERVIEW.md`) |
| `requirements.txt` | Consolidated pip dependency manifest |
| `Makefile` | Build task shortcuts |

### Module framework directories (root-level)

Each canonical module is a self-contained framework directory under
`modules/`. It owns contracts and reusable workflows, not project data.

```
modules/<module>/
  AGENTS.md              ← module contract: inputs, outputs, gate, skills, tools
  module.yaml            ← module registry manifest
  RUNBOOK.md             ← operator guide: concrete commands, paths, failure modes
  schemas/
  skills/
    <skill-name>/
      SKILL.md           ← reusable workflow program, loaded on demand
  tools/
    <script>.py          ← deterministic helper scripts owned by this module
  src/
  tests/
```

Canonical modules: `workspace`, `sources`, `transcription`, `manuscript`,
`interior`, `covers`, `publication`, `release`.

Legacy framework paths: `ingest/` (`sources`), `transcribe/`
(`transcription`), `proof/` (legacy proof support), `typeset/` (`manuscript`
and `interior`), `front-end/` (`publication`), and `final/` (`release`).

The old root framework directories remain as compatibility redirects for one
release cycle. New work should route through `modules/<module>/AGENTS.md`.
`proof/` remains only for legacy proof support and historical records. New proof
drafts are an `interior` rendering mode and write under
`projects/<project_id>/interior/output/proof/`.

### machinery/

All executable code and cross-stage infrastructure.

```
machinery/
  src/
    texgraph/            ← build system and editorial tools: CLI, config, parser, renderer, compiler, audit, metadata, PDF, archive, scan
  studio/
    backend/             ← FastAPI services (projects, builds, covers, previews)
    frontend/            ← React + Vite + TypeScript Studio interface
  tests/                 ← regression test suite
  docs/                  ← technical reference documents; Studio frontend dev lives in STUDIO_FRONTEND.md
  skills/                ← cross-stage infrastructure workflow programs
  tools/                 ← cross-stage infrastructure scripts
```

### projects/

Local project workspaces. Gitignored except tracked example projects.

```
projects/
  <project_id>/
    sources/
      raw/               ← renamed source files (<stable_name>.<ext>)
                            provenance records (<stable_name>.provenance.yaml)
      PROMOTION.yaml     ← module gate: sources approved for transcription
    transcription/
      PROMOTION.yaml     ← module gate: volumes transcribed and policy accepted
      <volume files, plans, metadata>
    manuscript/
      <audit reports, corrections, textual-review notes>
    interior/
      collection.yaml
      content/
      corrections/
      output/
        proof/
      PROMOTION.yaml     ← module gate: interior PDF embedded and approved
    covers/
      PROMOTION.yaml
      <cover assets and production files>
    publication/
    release/

    # compatibility-only paths accepted by aliases/migration:
    ingest/              ← sources legacy path
    transcribe/          ← transcription legacy path
      PROMOTION.yaml     ← module gate: volumes transcribed and policy accepted
      <volume files, plans, metadata>
    proof/               ← manuscript legacy support
    typeset/             ← interior legacy path
    front-end/           ← publication legacy path
    final/               ← release legacy path

  spectra_poems/         ← tracked example project (in git)
```

Build roots point at `projects/<project_id>/interior/`. During compatibility,
existing workspace `path` values may still point at `typeset/`; config
resolution checks both canonical and legacy interior roots.

---

## File Type Glossary

| File / Pattern | Meaning |
|---|---|
| `AGENTS.md` | Module contract or root dispatcher. Read first when entering a module. |
| `SKILL.md` | Reusable workflow program. Load on demand when the task matches. |
| `machinery/docs/README.md` | Canonical documentation index. |
| `machinery/docs/PROJECT_OVERVIEW.md` | Full project overview, formerly the root README body. |
| `machinery/docs/ONTOLOGY.md` | Comprehensive repo reference (this file). |
| `machinery/docs/PERSONA.md` | Editorial voice contract. Load only for generative/voice-led work. |
| `collection.yaml` | Project metadata and render_config. The build root's single config. |
| `workspace.yaml` | Maps project IDs to project/interior roots. Local, gitignored. |
| `workspace.example.yaml` | Template for workspace.yaml. In git. |
| `_meta.yaml` | Section metadata in a content directory (label, order, type). |
| `*.md` in `content/` | Poem or prose file with YAML front matter. |
| `*.tex.jinja2` | LaTeX document template rendered by the build system. |
| `*.xmp.jinja2` | PDF/X XMP metadata template. |
| `book.json` | Per-book derived metadata. Generated by `texgraph metadata`. |
| `book.md` | Volume/book manifest with YAML front matter. |
| `volume.md` | Volume-level manifest with YAML front matter. |
| `.ontology-baseline` | Stored git hash for ontology_check.py comparisons. Gitignored. |
| `PROMOTION.yaml` | Module gate record at `projects/<id>/<module>/PROMOTION.yaml`. Written by module commands or future `texgraph promote`. Read by `texgraph verify`. |
| `<stable_name>.provenance.yaml` | Source provenance record beside the renamed source file. Documents origin, rights, SHA-256 checksum, ingested_at timestamp, and notes. |
| `RUNBOOK.md` | Operator guide at a module root when present. Concrete commands, expected outputs, failure modes, and a walkthrough example. Complements `AGENTS.md`. |
| `RUN_REPORT.md` | Session log at `projects/<id>/RUN_REPORT.md`. Records what was executed, what was found, what was corrected, and what remains. Persists across sessions. |
| `STUDIO_FRONTEND.md` | Canonical Studio frontend development reference: scope, routes, current UI status, setup, and tests. |

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
    project_root: projects/project-slug  # canonical root, relative to workspace.yaml
    modules:
      sources: projects/project-slug/sources
      transcription: projects/project-slug/transcription
      manuscript: projects/project-slug/manuscript
      interior: projects/project-slug/interior
      covers: projects/project-slug/covers
      publication: projects/project-slug/publication
      release: projects/project-slug/release
    path: projects/project-slug/interior # compatibility alias for interior root
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

### PROMOTION.yaml — sources module

Written by `texgraph ingest rename`; approved manually until `texgraph promote`
exists. The `ingest` command name is retained as a compatibility alias.

```yaml
status: pending                    # pending | approved
sources:
  - stable_name: keats_1820_lamia-and-other-poems_upload.pdf
    stable_path: sources/raw/keats_1820_lamia-and-other-poems_upload.pdf
    original_name: Lamia 1820.pdf
    source_type: upload            # upload | internet_archive | scan | other
    rights: unknown                # unknown | public_domain | licensed | restricted
    access_confirmed: true
    checksum_sha256: "abc123..."
    ingested_at: "2026-05-26T14:00:00"
    page_count: 120                # optional
    notes: ""
```

Gate condition for `transcription`: `status == approved` and all sources have
`access_confirmed: true` with `stable_path` present on disk.

### PROMOTION.yaml — transcription module

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

Gate condition for `manuscript` and `interior`: `status == approved`,
`policy_accepted`, all volumes meet `all_statuses_at_least` floor, and
`uncertain_readings_accepted` if any open readings exist.

### PROMOTION.yaml — manuscript module

Written manually or by future `texgraph promote manuscript`. Gates nothing in
the current DAG (no downstream module requires an approved manuscript gate),
but is used by `texgraph promote manuscript` to record review completion and by
the manuscript `_check_proof` checker when called explicitly.

```yaml
status: pending                    # pending | approved
proof_pdf: interior/output/proof/proof.pdf  # path to the draft proof PDF relative to project root
textual_questions:
  open: 0                          # must be 0 before marking approved
  resolved: 12
page_count: 128                    # must be even for print
user_accepted_layout: true
```

### PROMOTION.yaml — proof support (legacy only)

```yaml
status: pending                    # pending | approved
proof_pdf: proof/output/proof.pdf  # legacy path relative to project root
textual_questions:
  open: 0                          # must be 0 for promotion
  resolved: 12
page_count: 128                    # must be even for print
user_accepted_layout: true
```

Legacy projects may retain proof promotion records for review history. Proof is
not a canonical pipeline stage. New proof drafts are a first-draft manuscript /
interior workflow and write to `interior/output/proof/`; `interior` unlocks
from approved `transcription`.

### PROMOTION.yaml — interior module

```yaml
status: pending                    # pending | approved
interior_pdf: interior/output/my-collection.pdf
fonts_embedded: true               # verified with pdffonts
user_approved_interior: true
```

Gate condition for `covers`, `publication`, and `release`: `status == approved`,
`interior_pdf` exists on disk, `fonts_embedded`, `user_approved_interior`.

### PROMOTION.yaml — release module

```yaml
status: pending                    # pending | approved
final_pdf: release/output/my-collection-final.pdf
```

Release records package approved upstream artifacts. They do not gate cover
production.

### Studio AuditRun

Returned by `POST /api/audit/run`. This is a read-only product readiness audit
contract for Studio, not a pipeline artifact and not a source-text audit.

```yaml
id: audit-<opaque>
created_at: "2026-06-06T00:00:00+00:00"
repo_root: C:/path/to/Texgraph
persona: burned_out_bay_area_engineer
frontend_framework: react
mode: read_only
target: texgraph_current_system
status: complete                    # pending | running | complete | failed
subagents:
  - id: pipeline-gates
    name: Pipeline/Gate Auditor
    category: Pipeline and gates
    status: warn                    # pass | warn | fail | blocked
    score: 6
    max_score: 10
    findings:
      - severity: high              # critical | high | medium | low
        claim: "Finding summary"
        evidence_refs: ["gate-code"]
        product_risk: "Risk to product readiness"
        recommended_next_step: "Next concrete action"
    evidence:
      - id: gate-code
        kind: file                  # file | command | test | doc | api | ui
        path: machinery/src/texgraph/promotions.py
        command: null
        observed: "Evidence summary"
    open_questions: []
report:
  one_sentence_product: "..."
  specific_user: "..."
  works_today_without_founder: []
  breaks_first: []
  next_risk_reducing_milestone: "..."
  verdict: promising_not_ready      # not_ready | promising_not_ready | narrowly_usable | ready_for_limited_users | product_ready
  category_scores: {}
  executive_summary: "..."
  highest_risk_assumption: "..."
  priority_findings: []
```

### Book manifest front matter (transcription projects)

```yaml
---
title: "Book Title"
book_order: 1
author: "Author Name"
publisher: "Publisher"
place: "City"
year: 1913
source_pdf: "sources/raw/<stable>.pdf"
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
source_pdf: "sources/raw/<stable>.pdf"
source_pages_scan: "1-2"
source_pages_printed: "i-ii"
status: transcribed
notes: ""
---
```

---

## Pipeline Architecture

```
workspace
  -> sources        source files, provenance, page counts
  -> transcription  poem text, source matter, volume plans, metadata
  -> manuscript     corrections, editorial assembly, proof drafts
  -> interior       layout and interior PDFs
      -> covers        cover production
      -> publication   e-reader, web, publication assets
  -> release        release packages, manifests, delivery
```

### Module ownership rules

- Each module **owns its artifacts**. It does not write to another module's
  directory without explicit user approval.
- Modules read from upstream artifacts; they never modify them.
- Promotion gates are always explicit. Silent cross-stage edits are forbidden.
- `release/` receives only user-approved artifacts from upstream.

### Content type routing within stages

When the task involves specific content types, load the matching sub-skill:

| Content type | Transcription skill | Manuscript skill | Interior skill |
|---|---|---|---|
| Verse (lyric, formal, free) | `modules/transcription/skills/poem-transcription` | `modules/manuscript/skills/poetry-proof` | `modules/interior/skills/poetry` |
| Prose (preface, essay, fiction) | `modules/transcription/skills/prose-transcription` | `modules/manuscript/skills/prose-proof` | `modules/interior/skills/prose` |
| Source paratext | `modules/transcription/skills/source-matter` | `modules/manuscript/skills/transcription-verification` | `modules/interior/skills/prose` |
| Documentation / repo structure | — | — | `technical-docs` (machinery) |

---

## Command Surface

The CLI is invoked as `texgraph`.

### Build and workspace commands

| Command | Stage | What it does |
|---|---|---|
| `texgraph build [--project <id>] [--draft]` | interior (`typeset` alias) | Parse → render → compile PDF |
| `texgraph proof-build [--project <id>]` | manuscript/interior | Render retained first-draft proof TeX/PDF under `interior/output/proof/` (`typeset/output/proof/` for unmigrated projects) |
| `texgraph watch [--project <id>]` | interior (`typeset` alias) | Auto-rebuild on file changes |
| `texgraph list` | workspace | List registered projects |
| `texgraph new poem "Title" [--section <id>]` | manuscript (`typeset` alias) | Scaffold poem file |
| `texgraph studio` | machinery | Launch FastAPI + React Studio |

### Pipeline gate commands

| Command | Stage | What it does |
|---|---|---|
| `texgraph verify <module> [--project <id>]` | all | Check upstream PROMOTION.yaml preconditions; legacy aliases resolve to canonical modules; exits 0 for modules with no upstream gate |
| `texgraph promote <module> [--project <id>] [--yes]` | all | Set status: approved in the module's PROMOTION.yaml; requires the file to exist; prompts for confirmation unless --yes |
| `texgraph ingest rename <file> --author A --year Y --title T [--source S] [--project <id>]` | sources (`ingest` alias) | Rename source to stable name, write provenance record, update sources PROMOTION.yaml |
| `texgraph modules list` | modules | List canonical modules and legacy aliases |
| `texgraph modules verify <module>` | modules | Verify a module using canonical module registry resolution |
| `texgraph migrate modules --project <id> --dry-run` | modules | Report planned project artifact directory migration |
| `texgraph migrate modules --project <id> --apply` | modules | Apply conflict-checked semantic module directory migration |

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
| `GET /api/projects/{id}/modules` | List canonical project modules and statuses |
| `GET /api/projects/{id}/modules/{module_id}` | Inspect a project module |
| `POST /api/projects/{id}/modules/{module_id}/verify` | Verify a module gate |
| `GET /api/projects/{id}/preview` | Generate preview |
| `POST /api/agent` | Agent endpoints |
| `POST /api/audit/run` | Run read-only product readiness audit |
| `GET/POST /api/covers` | Cover management |
| `GET /health` | Health check |

### Studio frontend routes

The canonical Studio frontend reference is `machinery/docs/STUDIO_FRONTEND.md`.

| Route | Purpose |
|---|---|
| `/` | Studio entry |
| `/ingest` | Ingest project picker |
| `/projects` | Continue Project |
| `/projects/new` | Create Project |
| `/projects/{id}/ingest` | Project-scoped Ingest Documents wireframe |
| `/projects/{id}` | Project editor |

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
| `pydantic` | texgraph/models.py, studio | Data validation |
| `mistune` | (available, not active) | Markdown parsing |

### Python packages (studio — `pyproject.toml` extra: `.[studio]`)

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

6. **Module isolation**: a module agent writes only to its module-owned project
   artifact directory. Cross-module writes require explicit user approval.

7. **Promotion gates are explicit**. User approval at each DAG edge is not
   optional and not automated.

8. **External knowledge must be cited** when it affects source facts, rights,
   editorial decisions, or production choices. It never overrides source evidence
   silently.

9. **`.env` is never committed**. It is gitignored and contains live credentials.

10. **`projects/` is gitignored** except explicitly tracked project exceptions
    listed in `.gitignore` as negation rules. Current tracked exception:
    `projects/spectra_poems/`.

11. **`texgraph` is the sole CLI entrypoint**. Keep the command name stable.

12. **`PROMOTION.yaml` is the machine-readable gate**. A stage does not begin
    work unless the upstream PROMOTION.yaml exists and passes `texgraph verify`.
    The file lives at `projects/<id>/<module>/PROMOTION.yaml`. Writing `status:
    approved` requires explicit user action via `texgraph promote <module>` (not
    yet implemented — stages 4–7 of the gate implementation plan).

13. **Stable source naming is the sources certification**. A file named according
    to the schema `<author>_<year>_<title>_<source>.<ext>` in `sources/raw/`
    certifies it has been processed. The original file is gone — `texgraph ingest
    rename` moves, not copies. Presence of the renamed file is the processing record.

---

## Installation and Setup

### First-time install

```powershell
# Create venv and install all dependencies
python -m venv .venv
.\.venv\Scripts\pip.exe install -e .
.\.venv\Scripts\pip.exe install -e ".[studio]"

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
