# Studio Module

Owns the interactive Studio product surface and module-facing Studio contracts.

## Scope

- Studio UI and API contracts as represented through module documentation.
- Product-facing workflows that coordinate workspace, sources, manuscript,
  interior, covers, publication, and release modules.
- Module-local Studio helpers and schemas.

## Artifact Boundary

This module documents and stages future Studio-facing module work. Do not edit
legacy `machinery/studio/` from this module without explicit scope approval.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers

