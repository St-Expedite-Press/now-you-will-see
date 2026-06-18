# Manuscript Module

Owns proofing, correction passes, editorial manuscript preparation, and content
readiness before interior production.

## Scope

- Proofing verse, prose, source matter, and editorial manuscript files.
- Applying approved correction passes to manuscript content.
- Preserving legacy proof workflows while moving new work toward manuscript
  readiness.

## Commands & Skills

- `texgraph verify-coverage [--project <id>]` — prove every transcription poem
  maps 1:1 to a built reading poem (no unbuilt, broken, or duplicated witnesses).
  Run after any content move, scaffold, or batch edit. Exits non-zero on a gap
  and is enforced by a test. See `RUNBOOK.md § Source coverage`.
- `texgraph proof-preview [--project <id>]` — render proof pages to PNG for
  visual review of layout and the keyed notes apparatus.
- Skills: `skills/poetry-proof/SKILL.md`, `skills/prose-proof/SKILL.md`,
  `skills/transcription-verification/SKILL.md`, `skills/persona-editorial/SKILL.md`.
- Context notes are keyed back-matter notes (no inline marks); lead each note
  with a line citation or `Form:` so it sets apart cleanly. See `RUNBOOK.md § Notes apparatus`.

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
