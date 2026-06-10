# Covers Module

Owns cover assets, cover production files, and cover readiness for release.

## Scope

- Cover concepts, source assets, generated assets, and production cover files.
- Cover unlock checks after interior approval.
- Print-vendor cover package preparation.

## Artifact Boundary

Stage artifacts live under `projects/<project_id>/covers/`. Read approved
interior outputs; do not modify interior artifacts from this module.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers

