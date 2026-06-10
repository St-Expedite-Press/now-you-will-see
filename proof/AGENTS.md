# Proof Workflows

Proof is now a first-draft mode of the `typeset` stage, not a separate pipeline
stage between transcription and typesetting.

Use `typeset/AGENTS.md` for routing and stage ownership. The proof directory
keeps reusable proofing skills and legacy project artifacts, but new draft TeX
and PDF builds belong under:

```
projects/<project_id>/typeset/output/proof/
```

## Use For

- Reusable proofing checklists and legacy correction records.
- Verse, prose, and transcription verification guidance loaded from the
  `proof/skills/` directory.

## Do Not Use For

- New proof draft builds. Use `texgraph proof-build --project <id>`, which writes
  to `typeset/output/proof/`.
- New promotion gates between transcribe and typeset. `texgraph verify typeset`
  now checks the transcribe gate directly.

## Local Skills

- `skills/poetry-proof/SKILL.md` — line-break, stanza, and indentation proof for verse
- `skills/prose-proof/SKILL.md` — paragraph integrity and type-tag proof for prose
- `skills/transcription-verification/SKILL.md` — cross-file status and metadata audit
- `skills/persona-editorial/SKILL.md` — editorial voice review
