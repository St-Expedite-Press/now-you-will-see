# Proof Stage

Owns proofing, verification, correction passes, and editorial voice review.

## Use For

- Auditing transcribed files against source pages.
- Checking statuses, page spans, forbidden markup, and metadata consistency.
- Editorial prose review through the configured persona.

## DAG Contract

Inputs:
- transcribed project text
- source scans or PDFs
- metadata and page-span records
- user-approved persona scope for editorial prose, if any

Outputs:
- audit reports
- correction records
- unresolved textual question list
- proof status notes

User gate:
- user accepts corrections, decides unresolved textual questions, and approves
  proof status before typeset or final promotion.

## Local Skills

- `skills/poetry-proof/SKILL.md` — line-break, stanza, and indentation proof for verse
- `skills/prose-proof/SKILL.md` — paragraph integrity and type-tag proof for prose
- `skills/transcription-verification/SKILL.md` — cross-file status and metadata audit
- `skills/persona-editorial/SKILL.md` — editorial voice review (load PERSONA.md first)

## Tools

- `texgraph audit projects/<project_id>/transcribe/volumes/<volume>/books/<book>`
- `texgraph metadata projects/<project_id>/transcribe/volumes --check`

Proof artifacts belong under `projects/<project_id>/proof/`, which is
local-only and ignored by Git.
