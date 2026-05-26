# Typeset Stage

Owns interior layout policy, buildable project roots, and production
build conventions.

## Use For

- Collection structure and `collection.yaml` conventions.
- Interior typography, layout regimes, templates, and proof PDF generation.
- Build verification for `projects/<project_id>/typeset/`.

## DAG Contract

Inputs:
- approved proof PROMOTION.yaml — run `texgraph verify typeset [--project <id>]` before beginning
- proof-approved text
- collection metadata
- trim and format
- layout/type regime
- inclusion/exclusion decisions

Outputs:
- buildable `typeset/` project
- TeX/PDF build artifacts
- build logs
- layout notes and blockers
- `projects/<project_id>/typeset/PROMOTION.yaml` — written on user approval

User gate:
- user approves trim, type regime, draft proof, and final interior before
  final packaging.

## Local Skills

- `skills/poetry/SKILL.md` — verse layout: stanza_skip, line environment, cycles, long-line handling
- `skills/prose/SKILL.md` — prose layout: paragraph convention, blockquote, section headings
- `skills/typesetting/SKILL.md` — render_config reference, build verification, vendor checks

## Tools

- `texgraph verify typeset [--project <id>]` — check proof gate before starting
- `texgraph list`
- `texgraph build --project <project_id> --draft`
- `texgraph watch`
- `texgraph new poem "Title" --section <section_id>`

Typeset files belong under `projects/<project_id>/typeset/`, which is
local-only and ignored by Git.
