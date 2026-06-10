# Publication Module

Owns e-reader, web, and publication-facing outputs.

## Scope

- Digital publication assets derived from approved manuscript or interior work.
- Web and e-reader output contracts.
- Publication-facing metadata and asset packaging before release.

## Artifact Boundary

Module artifacts live under `projects/<project_id>/publication/`. Read upstream
approved artifacts; do not rewrite source, manuscript, or interior artifacts.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
