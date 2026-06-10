# Release Module

Owns final release packaging, manifests, and delivery artifacts.

## Scope

- Collecting approved cover, interior, and publication outputs.
- Final manifests and release packages.
- Delivery readiness checks.

## Artifact Boundary

Module artifacts live under `projects/<project_id>/release/`. Release consumes
approved upstream artifacts and should not mutate them.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
