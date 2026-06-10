# Typeset Stage

Owns proof drafts, editorial correction application, layout decisions, retained
TeX artifacts, and production-grade interior PDF output.

Proof is not a separate downstream stage. It is the first-draft mode of
typesetting: a reviewable TeX/PDF pass produced from the manuscript before the
final production build.

## Use For

- Building proof drafts for editorial and layout review.
- Recording and applying proof corrections that affect the typeset manuscript.
- Finalising collection.yaml: publisher name, ISBN, final fonts, margins,
  trim size, and PDF/X document ID.
- Placing images: author photo, section ornaments, any in-text art.
- Running the production build to produce PDF/X-compliant output.
- Verifying font embedding and final interior approval.

## DAG Contract

Inputs:
- approved transcribe PROMOTION.yaml — run `texgraph verify typeset [--project <id>]` before beginning
- typeset manuscript at `projects/<project_id>/typeset/` (collection.yaml + content/)
- proof/editorial correction notes, if any
- final publisher metadata (ISBN, imprint, edition statement)
- any images to place (cover assets from covers/, author photo, ornaments)

Outputs:
```
projects/<project_id>/typeset/
  corrections/
    <topic>.md                  ← proof/layout correction notes and style sheets
  output/
    proof/
      tex/
        <slug>.tex              ← retained first-draft proof tex
      <slug>.pdf                ← proof draft PDF for review
    tex/
      <slug>.tex                ← final production tex (tracked)
    <slug>.pdf                  ← interior PDF (production quality, gitignored)
  PROMOTION.yaml
```

User gate:
- User reviews draft proof(s), corrections, trim, font, and layout.
- User confirms fonts are embedded (`pdffonts <interior_pdf>`).
- User approves final interior before cover assembly.

## Local Skills

- `skills/poetry/SKILL.md` — verse layout: stanza_skip, line environment, cycles
- `skills/prose/SKILL.md` — prose layout: paragraph convention, blockquote, headings
- `skills/typesetting/SKILL.md` — render_config reference, build verification, vendor checks
- `../proof/skills/poetry-proof/SKILL.md` — verse proof checklist for draft review
- `../proof/skills/prose-proof/SKILL.md` — prose proof checklist for draft review
- `../proof/skills/transcription-verification/SKILL.md` — cross-file status and metadata audit

## Tools

- `texgraph verify typeset [--project <id>]` — check transcribe gate before starting
- `texgraph proof-build --project <id>` — build retained first-draft proof under `typeset/output/proof/`
- `texgraph build --project <id>` — production build (PDF/X, multi-pass)
- `texgraph build --project <id> --draft` — quick check build
- `texgraph list` — list all configured projects
- `texgraph watch --project <id>` — live rebuild on file changes

Typeset output belongs under `projects/<project_id>/typeset/output/`.
Proof drafts are retained under `output/proof/`; final production TeX belongs
under `output/tex/`.
