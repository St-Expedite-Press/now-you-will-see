# Interior Module

Owns print interior layout, proof builds, production builds, and build-output
verification.

## Scope

- `collection.yaml` render configuration.
- Typeset proof drafts and production interior PDFs.
- Layout-specific skills for poetry, prose, and general typesetting.

## Artifact Boundary

Module artifacts live under `projects/<project_id>/interior/`, especially
`output/` for generated PDFs. Read manuscript content; avoid content edits unless
the user approves a correction pass.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows copied from legacy typeset workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers
