# Transcription Module

Owns source transcription, volume plans, source matter extraction, and
transcription readiness.

## Scope

- Transcribing source scans into structured project files.
- Tracking transcription status, uncertain readings, and volume metadata.
- Preparing artifacts that unlock manuscript work.

## Artifact Boundary

Module artifacts live under `projects/<project_id>/transcription/`. Read
approved source artifacts from `sources/`; do not alter them.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
