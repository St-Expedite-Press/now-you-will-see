# Texgraph

Texgraph is a local, stage-gated publishing system for serious literary
production. It turns Markdown/YAML manuscript files into LuaLaTeX-built PDFs,
and it organizes the larger editorial workflow around explicit stages:
source ingest, transcription, proof, typesetting, covers, publication front-end,
and final packaging.

It is designed for poets, translators, editors, and small presses who want
publication-grade output without handing their work to a platform or flattening
their editorial process into a single opaque export button.

## ELI5

Imagine you are making a real book.

You do not just throw pages into a magic printer. First you collect the sources.
Then you copy the text carefully. Then you check it. Then you lay it out. Then
you make the cover. Then you package the final files.

Texgraph is a set of labeled rooms for that work. Each room has its own rules,
tools, and checklist. Nothing moves to the next room until a person says it is
ready.

The computer helps with the boring and fragile parts: naming files, checking
metadata, building PDFs, keeping track of what is approved, and showing where
the project is blocked. The human still makes the editorial decisions.

## The Technical Case

Texgraph exists because literary production has a real systems problem:
manuscripts, scans, source evidence, corrections, layouts, covers, and release
files are usually managed as a loose pile of documents, manual steps, and memory.
That works for a single heroic operator. It does not work well for handoff,
repeatability, provenance, or multi-format production.

Texgraph makes the workflow explicit:

- A project has a stable directory shape under `projects/<project_id>/`.
- Each pipeline stage owns its artifacts and writes to its own stage directory.
- Promotion between stages is represented by `PROMOTION.yaml`.
- The CLI uses the same project model as Studio.
- The build system parses Markdown/YAML, renders Jinja2 LaTeX templates, and
  compiles with LuaLaTeX.
- Studio is a React/FastAPI control surface for project editing, builds, agent
  chat, covers, and product readiness audits.
- Repo-local `AGENTS.md` and `SKILL.md` files define how AI assistance should
  classify, route, and execute work without blurring stage boundaries.

The core design bet is simple: serious publishing software should preserve
editorial control and source provenance while making production repeatable.

## What Works Today

Texgraph currently has a working CLI and a partially working Studio app.

Built and usable:

- `texgraph build` parses collection content and builds PDFs through LuaLaTeX.
- `texgraph watch` rebuilds on file changes.
- `texgraph list` resolves projects from `workspace.yaml`.
- `texgraph new poem` scaffolds poem files in the correct section.
- `texgraph proof-build` renders a proof fragment tree and proof PDF from the
  typeset manuscript.
- `texgraph verify <stage>` checks upstream promotion preconditions.
- `texgraph ingest rename` moves source files into stable ingest names and
  writes provenance/promotion records.
- PDF/source helpers exist for inspection, text extraction, rendering, archive
  download, audits, metadata, page maps, plans, and scan reports.
- Studio backend exposes FastAPI routes for projects, sections, poems, versions,
  render config, builds, previews, covers, agent chat, and audit.
- Studio frontend is React/Vite/TypeScript with cards, graph, build, covers,
  agent, and audit views.
- The `spectra_poems` example project is tracked and buildable.

Current product readiness in plain terms: this is real engineering, especially
for CLI-driven print production. It is not yet a complete end-user product.

## What Is Not Finished

These gaps are intentional to name. They are not hidden.

- `texgraph promote <stage>` is not implemented yet. Users still need manual
  gate approval mechanics.
- The publication `front-end/` pipeline stage does not yet produce EPUB or web
  output.
- Studio does not yet expose full live `PROMOTION.yaml` gate state across the
  DAG.
- The Studio agent is chat-oriented and not yet classification-aware.
- Covers and final stages have contracts but limited local skills/tools.
- Test coverage is still thin relative to the CLI and Studio surface area.
- Production deployment is not the focus; Studio is currently local-first.

## Who This Is For

Texgraph is a good fit if you are:

- Producing poetry, translations, source editions, chapbooks, or small-press
  collections.
- Comfortable with a local Python environment and some YAML.
- Working from scans or historical sources where provenance matters.
- Trying to keep AI assistance inside explicit editorial and production rules.
- Willing to use a CLI while the Studio interface matures.

It is not a good fit yet if you need:

- A polished GUI-only app.
- EPUB export today.
- Cloud collaboration.
- A one-click publishing platform.
- A replacement for all book design judgment.

## Architecture

The project has three main layers.

### 1. Pipeline Stages

```text
project-create -> ingest -> transcribe -> proof -> typeset -> [covers, front-end] -> final
                                      proof -> final
```

Each stage has a root framework directory:

- `ingest/`
- `transcribe/`
- `proof/`
- `typeset/`
- `covers/`
- `front-end/`
- `final/`

Each project has matching local stage directories:

```text
projects/<project_id>/
  ingest/
  transcribe/
  proof/
  typeset/
  covers/
  front-end/
  final/
```

The invariant is important: a stage writes to its own directory. Cross-stage
writes require explicit user approval.

### 2. Build and Tooling Core

The Python package lives in `machinery/src/texgraph/`. It contains:

- CLI entrypoint: `texgraph`
- workspace/project resolution
- Markdown/YAML parsing
- Jinja2 rendering
- LuaLaTeX compilation
- PDF/source utilities
- metadata, audit, scan, and page-map helpers
- promotion gate verification

Shared infrastructure belongs in `machinery/`, not inside project data.

### 3. Studio

Studio is the local web control surface:

- backend: `machinery/studio/backend/` using FastAPI and Pydantic
- frontend: `machinery/studio/frontend/` using React, Vite, TypeScript, Zustand,
  Radix UI, CodeMirror, and React Flow

Studio is machinery. Publication-facing web/e-reader output belongs to the
pipeline `front-end/` stage. Studio frontend development details live in
`machinery/docs/STUDIO_FRONTEND.md`.

## Product Readiness Audit

Studio includes a read-only Product Readiness Audit dashboard. It is separate
from the editorial `/api/agent` chat.

The audit:

- inspects docs, CLI, backend, frontend, pipeline gates, tests, and operations
- runs non-mutating verification commands
- records failures as evidence
- scores subareas independently
- renders a plain readiness verdict and next risk-reducing milestone

Backend route:

```text
POST /api/audit/run
```

Frontend view:

```text
Studio -> Audit
```

The audit is intentionally unsentimental. It separates what exists now from what
is planned.

## Install

Requirements:

| Requirement | Used for |
|---|---|
| Python 3.11+ | CLI, backend, tests |
| TeX Live full or MiKTeX | PDF builds |
| EB Garamond or another system OpenType font | example build |
| poppler-utils | PDF/source inspection commands |
| Node.js 18+ | Studio frontend development/build |

Short path:

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -e .
Copy-Item workspace.example.yaml workspace.yaml
.\.venv\Scripts\texgraph.exe list
.\.venv\Scripts\texgraph.exe build --project spectra_poems --draft
```

For a fuller walkthrough, read [QUICKSTART.md](QUICKSTART.md).

## Verify

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest machinery\tests -q
```

Build the example project:

```powershell
.\.venv\Scripts\texgraph.exe build --project spectra_poems --draft
```

## Documentation Map

Start here:

- [QUICKSTART.md](QUICKSTART.md): install and first build
- [ONTOLOGY.md](ONTOLOGY.md): authoritative repo map, schemas, commands,
  invariants
- [AGENTS.md](AGENTS.md): request classification and routing
- [HANDOFF.md](HANDOFF.md): current state and pending work
- [machinery/docs/DAG_PIPELINE.md](machinery/docs/DAG_PIPELINE.md): pipeline
  node contracts
- [machinery/docs/STUDIO_FRONTEND.md](machinery/docs/STUDIO_FRONTEND.md): Studio
  frontend architecture, routes, development, and testing
- [machinery/docs/DATA_DICTIONARY.md](machinery/docs/DATA_DICTIONARY.md):
  stable conceptual contracts
- [machinery/docs/PROCEDURES.md](machinery/docs/PROCEDURES.md): operating
  procedures

## The Narrow Wedge

The credible current wedge is not "AI-native publishing platform." That would
overstate the implementation.

The credible wedge is:

> A local, stage-gated literary production pipeline that can build serious print
> interiors from structured Markdown/YAML while preserving source provenance and
> human approval.

Studio, audit dashboards, module agents, covers, EPUB, and final packaging build
outward from that wedge.

## License

MIT. See `pyproject.toml` for package metadata.
