# Typeset Stage

Owns final production layout: publisher preambles, cover integration, image
placement, and production-grade PDF/X output.

The proof stage produced the draft tex+pdf for editorial review. The typeset
stage takes the approved proof and produces the press-ready interior.

## Use For

- Finalising collection.yaml: publisher name, ISBN, final fonts, margins,
  trim size, and PDF/X document ID.
- Adding front matter pages that require final copy: copyright page, colophon.
- Placing images: author photo, section ornaments, any in-text art.
- Running the production build (no `--draft`) to produce PDF/X-compliant output.
- Verifying font embedding and PDF/X conformance.

## DAG Contract

Inputs:
- approved proof PROMOTION.yaml — run `texgraph verify typeset [--project <id>]` before beginning
- proof-approved tex artifact at `proof/output/tex/<slug>.tex`
- typeset manuscript at `projects/<project_id>/typeset/` (collection.yaml + content/)
- final publisher metadata (ISBN, imprint, edition statement)
- any images to place (cover assets from covers/, author photo, ornaments)

Outputs:
```
projects/<project_id>/typeset/
  output/
    tex/
      <slug>.tex                ← final production tex (tracked)
    <slug>.pdf                  ← interior PDF (production quality, gitignored)
  PROMOTION.yaml
```

User gate:
- User approves trim, font, and layout.
- User confirms fonts are embedded (`pdffonts <interior_pdf>`).
- User approves final interior before cover assembly.

## Local Skills

- `skills/poetry/SKILL.md` — verse layout: stanza_skip, line environment, cycles
- `skills/prose/SKILL.md` — prose layout: paragraph convention, blockquote, headings
- `skills/typesetting/SKILL.md` — render_config reference, build verification, vendor checks

## Tools

- `texgraph verify typeset [--project <id>]` — check proof gate before starting
- `texgraph build --project <id>` — production build (PDF/X, multi-pass)
- `texgraph build --project <id> --draft` — quick check build
- `texgraph list` — list all configured projects
- `texgraph watch --project <id>` — live rebuild on file changes

Typeset output belongs under `projects/<project_id>/typeset/output/`.
The tex artifact in `output/tex/` is tracked; the PDF is gitignored.
