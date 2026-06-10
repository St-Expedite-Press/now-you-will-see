# Proof Workflow Runbook

Proof is now a first-draft mode of the `typeset` stage.

Use this directory for reusable proofing skills and legacy correction records.
For new work, route through `typeset/AGENTS.md`.

## Current Flow

```powershell
.\.venv\Scripts\texgraph.exe verify typeset --project <id>
.\.venv\Scripts\texgraph.exe proof-build --project <id>
```

`proof-build` writes retained draft artifacts to:

```
projects/<project_id>/interior/output/proof/
  tex/
  <slug>.pdf
```

The draft PDF is a review artifact. Final interior approval is recorded in
`projects/<project_id>/interior/PROMOTION.yaml` after the production build,
font embedding check, and user approval.

## Legacy Records

Older projects may contain:

```
projects/<project_id>/manuscript/
  audit/
  corrections/
  output/
  PROMOTION.yaml
```

Do not create new proof promotion gates for current projects. Keep legacy files
only when they are needed for provenance or review history.

## Skills

- `modules/manuscript/skills/poetry-proof/SKILL.md`
- `modules/manuscript/skills/prose-proof/SKILL.md`
- `modules/manuscript/skills/transcription-verification/SKILL.md`
- `modules/manuscript/skills/persona-editorial/SKILL.md`
