# Manuscript Runbook

The manuscript stage owns the editorial reading edition: proofing, corrections,
and content readiness before interior typesetting. Proof drafts are produced by
the interior pipeline (`texgraph proof-build`); see `modules/interior/AGENTS.md`
for the build itself. This runbook covers manuscript-side operations.

## Current Flow

```powershell
.\.venv\Scripts\texgraph.exe verify typeset --project <id>
.\.venv\Scripts\texgraph.exe proof-build --project <id>
```

## Source coverage (no poem ever dropped)

Before signing off a reading edition, prove every transcription poem is built:

```powershell
.\.venv\Scripts\texgraph.exe verify-coverage --project <id>
```

It checks the `source:` links from reading poems to their transcription
witnesses — failing on any unbuilt, broken, or duplicated witness (exits
non-zero). The same check runs as a test, so CI fails if a poem goes missing.
This exists because a poem sequence once vanished silently; run it after any
content move, scaffold, or batch edit.

## Notes apparatus (reading edition)

Context notes are typeset as **keyed back-matter notes**, not inline footnotes:
no in-text marks; per-book "Notes to <Book>" sections group each poem's notes
under its title with a page reference, keyed by line number. Each note's leading
line citation or `Form:` label is set apart from the gloss. Editorial notes
should therefore lead with a line citation (`ll. 9–10 ('lemma'):`) or `Form:`
where applicable so the apparatus reads as structured entries.

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
