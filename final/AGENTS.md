# Final Stage

Owns release packaging and delivery checks.

## Use For

- Print-ready PDFs, checksums, release notes, and upload packages.
- Final handoff manifests and delivery verification.
- Confirming that draft proof artifacts have not been promoted accidentally.

## DAG Contract

Inputs:
- proof approval
- approved interior files
- approved cover files
- optional approved front-end deliverables
- vendor/release target

Outputs:
- release package
- delivery manifest
- checksums
- upload checklist
- final notes

User gate:
- user gives final signoff for the package and target.

## Local Skills

No local skills yet. Use `typeset/skills/typesetting/SKILL.md` for production
layout questions and `proof/skills/transcription-verification/SKILL.md` for
textual verification gates.

## Tools

- `texgraph build --project <project_id>`
- PDF inspection tools such as `pdffonts` when available.

Final artifacts belong under `projects/<project_id>/final/`, which is
local-only and ignored by Git.
