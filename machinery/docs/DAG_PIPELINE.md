# DAG Pipeline Contract

This document defines the end-to-end publishing graph. The graph exists so a
project can move from first source intake to release without hiding
module-specific decisions inside one opaque command.

## Principle

The pipeline is a directed acyclic graph with user-gated transitions. A stage
can prepare outputs for the next stage, but promotion requires explicit user
input. The system may recommend, validate, or package; it does not silently
decide.

Studio's Product Readiness Audit is deliberately outside this graph. It audits
the system and Studio surface; it does not promote project artifacts and does
not write `PROMOTION.yaml`.

## Graph

```text
workspace
  -> sources
  -> transcription
  -> manuscript
  -> interior
      -> covers
      -> publication
  -> release
```

## Promotion Records

Each module gate is enforced by a `PROMOTION.yaml` file at
`projects/<project_id>/<module>/PROMOTION.yaml`. A module may not begin work
until the upstream module's PROMOTION.yaml exists and passes `texgraph verify`.

**Implemented gates** (upstream → stage):

| Upstream | Stage | Command |
|---|---|---|
| sources | transcription | `texgraph verify transcription` (`transcribe` alias) |
| transcription | manuscript | `texgraph verify manuscript` (`proof` compatibility alias) |
| transcription | interior | `texgraph verify interior` (`typeset` alias) |
| interior | covers | `texgraph verify covers` |
| interior | publication | `texgraph verify publication` (`front-end` alias; checker still minimal) |
| interior | release | `texgraph verify release` (`final` alias) |

**Pending gates** (not yet implemented):
- publication module needs a fuller checker for EPUB/web deliverables
- `texgraph promote <module>` command (writes approved PROMOTION.yaml)

Implemented support command:
- `texgraph proof-build` renders a proof artifact tree and proof PDF from the
  interior manuscript.

See `ONTOLOGY.md § Data Schemas` for full PROMOTION.yaml schemas per stage.
See `machinery/src/texgraph/promotions.py` for the verification implementation.

## Node Contracts

### project-create

Purpose: create a project skeleton and register it in `workspace.yaml`.

Inputs:
- project ID
- title
- author/editor
- publication type
- intended outputs
- optional persona choice

Outputs:
- `projects/<project_id>/` module directories
- initial `projects/<project_id>/interior/collection.yaml`
- workspace registration

User gate:
- approve project ID, title, and initial stage structure

### sources

Purpose: acquire, rename, and document source material.

Inputs:
- source identifiers or files
- rights/provenance decisions
- naming policy

Outputs:
- renamed source files under `projects/<project_id>/sources/raw/` — stable name: `<author>_<year>_<title>_<source>.<ext>`
- provenance records (`<stable_name>.provenance.yaml`)
- `projects/<project_id>/sources/PROMOTION.yaml`

Commands:
- `texgraph ingest rename <file> --author A --year Y --title T`
- `texgraph verify sources`

User gate:
- approve source set and rights/provenance status

### transcription

Purpose: convert source material into documentary project text.

Inputs:
- approved sources PROMOTION.yaml (`texgraph verify transcription`)
- approved source files
- target volume/book/section
- transcription policy
- unresolved source questions

Outputs:
- transcribed text under `projects/<project_id>/transcription/`
- source matter files
- metadata and planning updates
- `projects/<project_id>/transcription/PROMOTION.yaml`

User gate:
- accept transcription policy and resolve uncertain readings or mark them open

### manuscript

Purpose: verify text against source evidence, record corrections, and maintain
the build manuscript.

Inputs:
- approved transcription PROMOTION.yaml
- transcribed text
- source images or PDFs
- metadata
- persona boundary for editorial prose only

Outputs:
- corrected manuscript files
- audit reports and correction notes
- retained proof drafts under `projects/<project_id>/interior/output/proof/`

User gate:
- accept corrections and decide unresolved textual questions.

### interior

Purpose: prepare buildable book interiors.

Inputs:
- approved transcription/manuscript state (`texgraph verify interior`; `typeset` alias)
- corrected manuscript text
- collection metadata
- trim size
- type/layout regime
- inclusion decisions

Outputs:
- `collection.yaml`
- content directories
- draft/final TeX/PDF artifacts
- build logs and layout notes
- `projects/<project_id>/interior/PROMOTION.yaml`

User gate:
- approve format, type regime, draft proof, and final interior

### covers

Purpose: produce and verify cover assets.

Inputs:
- approved interior PROMOTION.yaml (`texgraph verify covers`)
- title/author/metadata
- trim and page count from interior
- cover assets
- vendor requirements
- visual direction

Outputs:
- cover source files
- cover proofs
- vendor-ready cover files
- cover manifest

User gate:
- approve visual direction, proof, and vendor file

### publication

Purpose: produce publication-facing web/static materials.

Inputs:
- project metadata
- approved copy
- optional approved cover assets
- public audience and call-to-action

Outputs:
- reader/publication front-end files
- static assets
- launch notes

User gate:
- approve public copy, media, and launch state

### release

Purpose: collect approved artifacts for release or handoff.

Inputs:
- approved interior PROMOTION.yaml (`texgraph verify release`; `final` alias)
- interior approval
- cover approval (if covers stage complete)
- optional front-end approval
- vendor target

Outputs:
- release package
- checksums
- delivery manifest
- upload checklist
- final notes
- `projects/<project_id>/release/PROMOTION.yaml`

User gate:
- final signoff
