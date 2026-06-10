---
name: prose
description: Typeset prose sections (type: prose) in a texgraph collection. Use for paragraph spacing, quotation/epigraph blocks, section headings, and verifying that prose content renders correctly alongside verse.
---

# Prose Typesetting

## Use When

Load this skill when the typeset task involves prose content:

- Files with `type: prose` are not rendering correctly
- Configuring paragraph spacing or first-line indent for prose sections
- Handling block quotations, epigraphs, or prefatory matter
- Section headings within a prose piece
- Mixed collections (prose sections alongside verse sections)
- Verifying `type: prose` content builds without verse-environment artifacts

Do not use for: verse content (`type: poem`, `type: poem-cycle`), cover assets,
or e-reader/HTML output.

## Required Reads

Before making layout decisions, read:

- `projects/<project_id>/interior/collection.yaml` — active `render_config`
- `ONTOLOGY.md § Data Schemas` — prose front matter fields
- `ONTOLOGY.md § Command Surface` — build and watch commands

## Prose Front Matter

```yaml
---
title: "Preface"
type: prose
order: 1
subtitle: ""        # optional
epigraph: ""        # optional
dedication: ""      # optional
---
```

`type: prose` disables the verse environment. Body text is typeset as standard
paragraphs with first-line indent (or space-between-paragraphs, depending on
the active template convention). Do not set `type: poem` on prose content.

## Paragraph Convention

Standard literary prose uses first-line indent with no inter-paragraph space.
If the project requires space-between style (e.g., essays, digital-first prose),
set `para_style: spaced` in `render_config` if supported, or note the deviation
in a template comment.

No rendered paragraph convention should require editing source `.md` files.

## Block Quotations and Epigraphs

In body Markdown, block quotations use standard `>` blockquote syntax:

```markdown
> This is a block quotation spanning
> multiple lines.
```

For poem-level epigraphs, use the `epigraph` YAML field. For inline epigraphs
within prose body, use blockquote syntax. Both render via the LaTeX
`\epigraph` command or equivalent.

## Section Headings Within Prose

Internal section headings use standard Markdown heading levels:

- `## Heading` — major section within a prose piece
- `### Sub-heading` — subsection

Do not use `#` (reserved for document title). The build system maps heading
levels to LaTeX `\section` / `\subsection` commands.

## Mixed Collections (Prose + Verse)

When a collection contains both `type: prose` and `type: poem` files:

1. Order is governed by `order` field within each section.
2. The build system switches environments per file type automatically.
3. Prose `line_spread` defaults to the same `render_config` value as verse —
   adjust only if the visual result is incorrect.
4. Section `_meta.yaml` type governs section rendering, not individual file type.

## Build and Preview

```powershell
.\.venv\Scripts\texgraph.exe build --project <id> --draft
.\.venv\Scripts\texgraph.exe watch --project <id>
```

Check output in `projects/<project_id>/interior/output/`.

## Guardrails

- Never alter source `.md` content for typesetting reasons.
- `type:` field in YAML is a content classification — change it only if
  the content is genuinely misclassified.
- Do not force verse line breaks (`\\`, `<br>`) into prose content.
- Template changes require a comment explaining why the default was insufficient.
