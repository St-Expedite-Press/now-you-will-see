# Transcribe Stage

Owns transcription, source matter, volume planning, and project-level editorial
planning.

## Use For

- Poem and source-matter transcription.
- Volume plans, book checklists, transcription status, and metadata hygiene.
- Project publication plans that organize transcribed material.

## DAG Contract

Inputs:
- approved ingest PROMOTION.yaml — run `texgraph verify transcribe [--project <id>]` before beginning
- approved source files from `projects/<project_id>/ingest/raw/`
- target volume, book, section, or item
- transcription policy
- source page map or source scope

Outputs:
- documentary transcription under `projects/<project_id>/transcribe/`
- source matter files
- metadata and book/volume status updates
- unresolved-reading notes
- `projects/<project_id>/transcribe/PROMOTION.yaml` — written on user approval

User gate:
- user approves transcription policy and either resolves uncertain readings or
  accepts them as recorded uncertainties before proof promotion.

## Local Skills

- `skills/poem-transcription/SKILL.md` — verse transcription from scan
- `skills/prose-transcription/SKILL.md` — prose/paratext transcription from scan
- `skills/source-matter/SKILL.md` — front and back matter, dedicatory material
- `skills/volume-planning/SKILL.md` — volume structure and checklist scaffolding
- `skills/project-planning/SKILL.md` — multi-volume project planning

## Tools

- `texgraph verify transcribe [--project <id>]` — check ingest gate before starting
- `texgraph metadata projects/<project_id>/transcribe/volumes --write --check`
- `texgraph scan projects/<project_id>/transcribe/volumes --output projects/<project_id>/transcribe/metadata/source_matter_inventory.md`
- `texgraph plan projects/<project_id>/transcribe/project_plan/PROJECT_PLAN.md --check`
- `texgraph page-map --offset <n> --printed "<ranges>"`

Transcription files belong under `projects/<project_id>/transcribe/`, which is
local-only and ignored by Git.
