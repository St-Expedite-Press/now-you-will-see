# Manuscript Module

Owns proofing, correction passes, editorial manuscript preparation, and content
readiness before interior production.

## Scope

- Proofing verse, prose, source matter, and editorial manuscript files.
- Applying approved correction passes to manuscript content.
- Preserving legacy proof workflows while moving new work toward manuscript
  readiness.

## Artifact Boundary

Primary manuscript artifacts live under `projects/<project_id>/manuscript/`.
Interior build content lives under `projects/<project_id>/interior/content/`.
Legacy proof records may remain under `projects/<project_id>/manuscript/` during the
one-release compatibility window.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows copied from legacy proof workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
