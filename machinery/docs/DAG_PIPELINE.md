# DAG Pipeline Contract

This document defines the end-to-end publishing graph. The graph exists so a
project can move from first source intake to final release without hiding
stage-specific decisions inside one opaque command.

## Principle

The pipeline is a directed acyclic graph with user-gated transitions. A stage
can prepare outputs for the next stage, but promotion requires explicit user
input. The system may recommend, validate, or package; it does not silently
decide.

## Graph

```text
project-create
  -> ingest
  -> transcribe
  -> proof
  -> typeset
  -> final

typeset -> covers -> final
typeset -> front-end -> final
proof   -> final
```

## Promotion Records

Each stage gate is enforced by a `PROMOTION.yaml` file at
`projects/<project_id>/<stage>/PROMOTION.yaml`. A stage may not begin work
until the upstream stage's PROMOTION.yaml exists and passes `texgraph verify`.

**Implemented gates** (upstream → stage):

| Upstream | Stage | Command |
|---|---|---|
| ingest | transcribe | `texgraph verify transcribe` |
| transcribe | proof | `texgraph verify proof` |
| proof | typeset | `texgraph verify typeset` |
| typeset | final | `texgraph verify final` |
| final | covers | `texgraph verify covers` (requires `cover_unlock.unlocked: true`) |

**Pending gates** (not yet implemented):
- front-end stage has no formal verify gate yet
- `texgraph promote <stage>` command (writes approved PROMOTION.yaml) — step 5 of gate plan
- `texgraph proof-build` command — step 4 of gate plan

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
- `projects/<project_id>/` stage directories
- initial `projects/<project_id>/typeset/collection.yaml`
- workspace registration

User gate:
- approve project ID, title, and initial stage structure

### ingest

Purpose: acquire, rename, and document source material.

Inputs:
- source identifiers or files
- rights/provenance decisions
- naming policy

Outputs:
- renamed source files under `projects/<project_id>/ingest/raw/` — stable name: `<author>_<year>_<title>_<source>.<ext>`
- provenance records (`<stable_name>.provenance.yaml`)
- `projects/<project_id>/ingest/PROMOTION.yaml`

Commands:
- `texgraph ingest rename <file> --author A --year Y --title T`
- `texgraph verify ingest`

User gate:
- approve source set and rights/provenance status

### transcribe

Purpose: convert source material into documentary project text.

Inputs:
- approved ingest PROMOTION.yaml (`texgraph verify transcribe`)
- approved source files
- target volume/book/section
- transcription policy
- unresolved source questions

Outputs:
- transcribed text under `projects/<project_id>/transcribe/`
- source matter files
- metadata and planning updates
- `projects/<project_id>/transcribe/PROMOTION.yaml`

User gate:
- accept transcription policy and resolve uncertain readings or mark them open

### proof

Purpose: verify text against source evidence and record corrections.

Inputs:
- approved transcribe PROMOTION.yaml (`texgraph verify proof`)
- transcribed text
- source images or PDFs
- metadata
- persona boundary for editorial prose only

Outputs:
- audit reports
- correction lists
- proof notes
- verified or blocked status markers
- `projects/<project_id>/proof/PROMOTION.yaml`

User gate:
- accept corrections, decide unresolved textual questions, approve proof status

### typeset

Purpose: prepare buildable book interiors.

Inputs:
- approved proof PROMOTION.yaml (`texgraph verify typeset`)
- proofed text
- collection metadata
- trim size
- type/layout regime
- inclusion decisions

Outputs:
- `collection.yaml`
- content directories
- draft/final TeX/PDF artifacts
- build logs and layout notes
- `projects/<project_id>/typeset/PROMOTION.yaml`

User gate:
- approve format, type regime, draft proof, and final interior

### covers

Purpose: produce and verify cover assets.

Inputs:
- approved final PROMOTION.yaml with `cover_unlock.unlocked: true` (`texgraph verify covers`)
- title/author/metadata
- trim and page count from typeset
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

### front-end

Purpose: produce publication-facing web/static materials.

Inputs:
- project metadata
- approved copy
- approved cover assets
- release status
- public audience and call-to-action

Outputs:
- reader/publication front-end files
- static assets
- launch notes

User gate:
- approve public copy, media, and launch state

### final

Purpose: collect approved artifacts for release or handoff.

Inputs:
- approved typeset PROMOTION.yaml (`texgraph verify final`)
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
- `projects/<project_id>/final/PROMOTION.yaml` with `cover_unlock.unlocked: true`

User gate:
- final signoff
