# Sources Module

Owns source acquisition, source registration, provenance, and ingest readiness.

## Scope

- Finding, downloading, renaming, and recording source files.
- Source provenance and access checks.
- Source artifacts that unlock transcription.

## Artifact Boundary

Module artifacts live under `projects/<project_id>/sources/`. Do not write
downstream transcription or manuscript files from this module without a user
gate.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
