# Transcribe Stage

Owns transcription, source matter, volume planning, and project-level editorial
planning.

## Use For

- Poem and source-matter transcription.
- Volume plans, book checklists, transcription status, and metadata hygiene.
- Project publication plans that organize transcribed material.

## DAG Contract

Inputs:
- approved ingest sources
- target volume, book, section, or item
- transcription policy
- source page map or source scope

Outputs:
- documentary transcription under `projects/<project_id>/transcribe/`
- source matter files
- metadata and book/volume status updates
- unresolved-reading notes

User gate:
- user approves transcription policy and either resolves uncertain readings or
  accepts them as recorded uncertainties before proof promotion.

## Local Skills

- `skills/poem-transcription/SKILL.md`
- `skills/source-matter/SKILL.md`
- `skills/volume-planning/SKILL.md`
- `skills/project-planning/SKILL.md`

## Tools

- `tools/create_fletcher_subprojects.py`
- `fletcher metadata projects/<project_id>/transcribe/volumes --write --check`
- `fletcher scan projects/<project_id>/transcribe/volumes --output projects/<project_id>/transcribe/metadata/source_matter_inventory.md`
- `fletcher plan projects/<project_id>/transcribe/project_plan/PROJECT_PLAN.md --check`
- `fletcher page-map --offset <n> --printed "<ranges>"`

Transcription files belong under `projects/<project_id>/transcribe/`, which is
local-only and ignored by Git.
