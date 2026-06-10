# Covers Stage

Owns cover-art policy, cover assets, style records, and cover production notes.

## Use For

- Cover source assets and generated cover files.
- Cover style records, active regime references, and vendor cover checks.
- Project-specific cover overrides.

## DAG Contract

Inputs:
- approved interior PROMOTION.yaml — run `texgraph verify covers [--project <id>]` before beginning
- project title, author/editor, imprint, and metadata
- approved trim and page count from interior/typeset output
- source cover assets or requested visual direction
- vendor requirements

Outputs:
- cover working files
- cover proofs
- vendor-ready cover files
- cover manifest or notes
- `projects/<project_id>/covers/PROMOTION.yaml` — gate pending implementation

User gate:
- user approves visual direction, selected assets, cover proof, and vendor file.

## Local Skills

No local skills yet. For typography decisions that carry over to covers,
read `typeset/skills/poetry/SKILL.md` or `typeset/skills/prose/SKILL.md`
as appropriate for the content type.

## Tools

- `texgraph verify covers [--project <id>]` — check the approved interior gate before starting
- Studio cover endpoints under `/api/projects/{project_id}/covers`.
- Project cover assets under `projects/<project_id>/covers/`.

Cover files belong under `projects/<project_id>/covers/`, which is local-only
and ignored by Git.
