# Covers Stage

Owns cover-art policy, cover assets, style records, and cover production notes.

## Use For

- Cover source assets and generated cover files.
- Cover style records, active regime references, and vendor cover checks.
- Project-specific cover overrides.

## DAG Contract

Inputs:
- project title, author/editor, imprint, and metadata
- approved trim and page count from typeset
- source cover assets or requested visual direction
- vendor requirements

Outputs:
- cover working files
- cover proofs
- vendor-ready cover files
- cover manifest or notes

User gate:
- user approves visual direction, selected assets, cover proof, and vendor file.

## Local Skills

No local skills yet. Use `typeset/skills/typesetting/SKILL.md` for typography
regime decisions that affect covers.

## Tools

- Studio cover endpoints under `/api/projects/{project_id}/covers`.
- Project cover assets under `projects/<project_id>/covers/`.

Cover files belong under `projects/<project_id>/covers/`, which is local-only
and ignored by Git.
