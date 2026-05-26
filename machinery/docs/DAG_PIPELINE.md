# DAG Pipeline Contract

This document defines the intended end-to-end publishing graph. The graph exists
so a project can move from first source intake to final release without hiding
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

Purpose: acquire and document source material.

Inputs:
- source identifiers or files
- rights/provenance decisions
- naming policy

Outputs:
- raw source files under `projects/<project_id>/ingest/`
- source manifest entries
- page counts and provenance notes

User gate:
- approve source set and rights/provenance status

### transcribe

Purpose: convert source material into documentary project text.

Inputs:
- approved source files
- target volume/book/section
- transcription policy
- unresolved source questions

Outputs:
- transcribed text under `projects/<project_id>/transcribe/`
- source matter files
- metadata and planning updates

User gate:
- accept transcription policy and resolve uncertain readings or mark them open

### proof

Purpose: verify text against source evidence and record corrections.

Inputs:
- transcribed text
- source images or PDFs
- metadata
- persona boundary for editorial prose only

Outputs:
- audit reports
- correction lists
- proof notes
- verified or blocked status markers

User gate:
- accept corrections, decide unresolved textual questions, approve proof status

### typeset

Purpose: prepare buildable book interiors.

Inputs:
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

User gate:
- approve format, type regime, draft proof, and final interior

### covers

Purpose: produce and verify cover assets.

Inputs:
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
- proof approval
- interior approval
- cover approval
- optional front-end approval
- vendor target

Outputs:
- release package
- checksums
- delivery manifest
- upload checklist
- final notes

User gate:
- final signoff

## Promotion Records

Each promotion should eventually leave a machine-readable record:

```yaml
from_stage: proof
to_stage: typeset
project_id: example-project
approved_by: user
approved_at: 2026-05-26T00:00:00Z
inputs:
  - path: projects/example-project/transcribe
outputs:
  - path: projects/example-project/typeset
notes: ""
```

The current repo documents this contract. It does not yet implement automated
promotion records.
