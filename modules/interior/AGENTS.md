# Interior Module

Owns print interior layout, proof builds, production builds, and build-output
verification.

## Scope

- `collection.yaml` render configuration.
- Typeset proof drafts and production interior PDFs.
- Layout-specific skills for poetry, prose, and general typesetting.

## Commands & Skills

- `texgraph proof-build [--project <id>] [--config <sheet>] [--print-ready]` —
  the omnibus interior pipeline (`proof_*` templates). `--config` builds a trim
  variant (hardcover/softcover); `--print-ready` emits even-page PDF/X-3 to
  `output/print/<format>/`. See `RUNBOOK.md § Proof build`.
- `texgraph proof-preview [--project <id>] [--pages <spec>] [--sample <n>]` —
  render structural pages to PNG for the mandatory visual review (poppler).
- Skills: `skills/typesetting/SKILL.md` (render_config, page modes, placement
  knobs, `stanza_skip` lever + per-poem override, PDF/X), `skills/poetry/SKILL.md`,
  `skills/prose/SKILL.md`.
- Page-mode (`one-per-page` vs `flow`) and placement are decided in TeX by
  measured poem height; never reintroduce a Python line-count proxy.

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
