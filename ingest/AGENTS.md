# Ingest Stage

Owns source acquisition and intake.

## Use For

- Finding, naming, downloading, or registering source files.
- PDF provenance, source manifests, and source page-count checks.
- Intake policy shared across projects.

## DAG Contract

Inputs:
- source identifiers, URLs, files, or user-provided source leads
- rights/access notes from the user
- naming policy or stable-title preference

Outputs:
- renamed source files under `projects/<project_id>/ingest/raw/`
- provenance records (`<stable_name>.provenance.yaml`)
- `projects/<project_id>/ingest/PROMOTION.yaml` — written by `texgraph ingest rename`; approved by user

User gate:
- user approves the source set, rights/access status, and stable naming before
  transcribe work begins.

## Local Skills

- `skills/source-intake/SKILL.md`

## Tools

- `texgraph ingest rename <file> --author A --year Y --title T [--source S] [--project <id>]`
- `texgraph verify ingest [--project <id>]` — check ingest PROMOTION.yaml
- `texgraph archive files <identifier>`
- `texgraph archive download <identifier> <filename> projects/<project_id>/ingest/raw/<stable>.pdf`
- `texgraph pdf info <pdf>`
- `texgraph pdf render <pdf> --first <n> --last <n> --prefix <prefix>`
- `texgraph pdf text <pdf> --first <n> --last <n>`

Project source files belong under `projects/<project_id>/ingest/`, which is
local-only and ignored by Git.
