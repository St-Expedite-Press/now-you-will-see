---
name: poetry
description: Typeset verse (lyric, formal, free, poem-cycle) using the texgraph build system. Use when configuring stanza spacing, line environment, poem title display, indentation, long-line handling, or cycle section headings in a collection build.
---

# Poetry Typesetting

## Use When

Load this skill when the typeset task involves verse content:

- Adjusting `stanza_skip` or `line_spread` for verse
- Diagnosing line-break or stanza-break rendering issues
- Setting up poem title display, subtitle, epigraph, or dedication
- Handling indented lines, run-overs, or very long lines
- Configuring poem cycles (multi-section poems with internal headings)
- Verifying that `type: poem` or `type: poem-cycle` content builds correctly

Do not use for: prose sections (`type: prose`), cover assets, or e-reader output.

## Required Reads

Before making layout decisions, read:

- `projects/<project_id>/typeset/collection.yaml` — active `render_config` values
- `ONTOLOGY.md § Data Schemas` — `collection.yaml` and poem front matter fields
- `ONTOLOGY.md § Command Surface` — build and watch commands

## render_config Keys for Verse

| Key | Controls | Verse guidance |
|---|---|---|
| `stanza_skip` | Vertical gap between stanzas | `1.2ex`–`1.8ex` for lyric; reduce for very short poems |
| `line_spread` | Leading multiplier | `1.1` for tight lyric; `1.15`–`1.2` for long-lined free verse |
| `fontsize` | Base type size | `11pt` standard; `10pt` for dense collections |
| `inner_margin` / `outer_margin` | Available line length | Narrow outer margins shorten measure; increase for long-lined poems |

Change `render_config` only in `collection.yaml`. Do not hardcode geometry in templates.

## Verse Environment

The build system wraps poem body text in a verse environment. Stanzas are
separated by blank lines in source Markdown. Do not insert `\\` or `<br>` for
line breaks — the verse environment handles this.

Leading spaces in source lines produce indentation in the rendered output.
Two leading spaces produce one indentation level. Do not use tabs.

## Long Lines

When a poem line exceeds the text measure:

1. Check that `outer_margin` is not excessive. Reduce by `0.125in` increments.
2. If the line is genuinely long, allow a run-over: add two extra leading spaces
   to the continuation to signal a run-over indent.
3. Do not break the line at an arbitrary point for typographic convenience.
4. Do not alter the source poem file for typesetting reasons.

## Poem Titles and Front Matter Fields

| YAML field | Rendered as | Notes |
|---|---|---|
| `title` | Poem title heading | Required |
| `subtitle` | Sub-heading below title | Omit field if empty |
| `epigraph` | Block quote before body | Single string; line breaks via `\n` |
| `dedication` | Dedication line | Omit if empty |
| `order` | Sequence within section | Integer; governs sort order |

## Poem Cycles (`type: poem-cycle`)

A poem cycle is a single Markdown file with internal section headings:

```markdown
## I.

First section body.

## II.

Second section body.
```

Use `## Roman.` or `## Title` headings. The build system renders cycle headings
as sub-poem titles within the containing verse environment. Do not split a cycle
into multiple files unless the section headings appear as separate contents-page
entries in the source.

## Build and Preview

```powershell
# Draft build (fast — skips PDF/X pass)
.\.venv\Scripts\texgraph.exe build --project <id> --draft

# Watch mode (rebuilds on file save)
.\.venv\Scripts\texgraph.exe watch --project <id>
```

Verify output in `projects/<project_id>/typeset/output/`.

## Guardrails

- Never alter source poem `.md` files for typesetting reasons.
- Never alter YAML front matter for typesetting reasons.
- `render_config` changes belong in `collection.yaml` only.
- Do not invent values not derivable from the current project's `collection.yaml`.
- If a layout problem requires a template change, record the reason as a comment
  in the template, not in a separate file.
