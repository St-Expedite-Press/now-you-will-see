# Workspace Module

Owns project registration, workspace discovery, and project creation contracts.

## Scope

- Local workspace metadata and project lookup behavior.
- Project-level scaffolding before source ingest begins.
- Compatibility notes for legacy workspace commands.

## Artifact Boundary

Writes should target workspace-level module code or `projects/<project_id>/`
scaffolding only when explicitly requested by the user.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers

