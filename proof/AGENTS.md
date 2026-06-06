# Proof Stage

Owns the audit pass, editorial corrections, and the draft proof build.
The proof build is the primary output of this stage: a tex artifact and draft PDF
that the user reviews before the typeset stage begins.

## Use For

- Auditing transcribed files against source scans (line-by-line poem proof).
- Recording and resolving textual questions.
- Checking statuses, page spans, forbidden markup, and metadata consistency.
- Building the draft proof PDF for editorial review.

## DAG Contract

Inputs:
- approved transcribe PROMOTION.yaml — run `texgraph verify proof [--project <id>]` before beginning
- transcribed poem files under `projects/<project_id>/transcribe/`
- source PDFs at `projects/<project_id>/ingest/raw/`

Outputs:
```
projects/<project_id>/proof/
  audit/
    <book>_audit.json           ← texgraph audit --json
  corrections/
    <book>_corrections.md       ← textual question log
  output/
    tex/
      <slug>.tex                ← proof tex artifact (tracked)
    <slug>.pdf                  ← draft proof PDF (gitignored — for review only)
  PROMOTION.yaml
```

User gate:
- User reviews the proof PDF.
- All textual questions resolved.
- User approves: sets `status: approved`, `user_accepted_layout: true` in PROMOTION.yaml.

## Local Skills

- `skills/poetry-proof/SKILL.md` — line-break, stanza, and indentation proof for verse
- `skills/prose-proof/SKILL.md` — paragraph integrity and type-tag proof for prose
- `skills/transcription-verification/SKILL.md` — cross-file status and metadata audit
- `skills/persona-editorial/SKILL.md` — editorial voice review

## Tools

- `texgraph verify proof [--project <id>]` — check transcribe gate
- `texgraph audit <book_dir> [--json]` — structural audit
- `texgraph metadata <volumes_dir> --check` — metadata consistency
- `texgraph pdf render <pdf> --first N --last N --prefix P` — render source pages for comparison
- `texgraph proof-build --project <id>` — draft build → proof/output/
- `texgraph verify typeset [--project <id>]` — confirm proof gate passes after promotion
