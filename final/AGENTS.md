# Final Stage

Owns release packaging and delivery checks.

## Use For

- Print-ready PDFs, checksums, release notes, and upload packages.
- Final handoff manifests and delivery verification.
- Confirming that draft proof artifacts have not been promoted accidentally.

## DAG Contract

Inputs:
- approved typeset PROMOTION.yaml — run `texgraph verify final [--project <id>]` before beginning
- approved interior files from typeset
- approved cover files (if covers stage complete)
- optional approved front-end deliverables
- vendor/release target

Outputs:
- release package
- delivery manifest
- checksums
- upload checklist
- final notes
- `projects/<project_id>/final/PROMOTION.yaml` — includes `cover_unlock.unlocked: true` to gate covers stage

User gate:
- user gives final signoff for the package and target.

## Local Skills

No local skills yet. For final production checks, read:
- `proof/skills/transcription-verification/SKILL.md` — textual verification gate
- `typeset/skills/poetry/SKILL.md` or `typeset/skills/prose/SKILL.md` — layout questions

## Tools

- `texgraph verify final [--project <id>]` — check typeset gate before starting
- `texgraph build --project <project_id>`
- `pdffonts` (verify font embedding before submission)

Final artifacts belong under `projects/<project_id>/final/`, which is
local-only and ignored by Git.
