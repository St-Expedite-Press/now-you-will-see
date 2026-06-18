# Transcription Module

Owns source transcription, volume plans, source matter extraction, and
transcription readiness.

## Scope

- Transcribing source scans into structured project files.
- Tracking transcription status, uncertain readings, and volume metadata.
- Preparing artifacts that unlock manuscript work.

## Coverage Contract

Reading-edition poems link back to their transcription witness through a
`source:` field. Renaming, moving, or deleting a poem under a `poems/` directory
breaks that link and can drop a poem from the built edition. After any such
change, run `texgraph verify-coverage --project <id>` (manuscript module) to
confirm the reading edition still covers every witness 1:1.

## Artifact Boundary

Module artifacts live under `projects/<project_id>/transcription/`. Read
approved source artifacts from `sources/`; do not alter them.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
