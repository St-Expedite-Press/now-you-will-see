# Front-End Stage

Owns publication-facing front-end deliverables.

## Use For

- Project publication sites, reader-facing assets, and static front-end outputs.
- Front-end artifacts that ship with or promote a publication.

## DAG Contract

Inputs:
- approved project metadata and typeset output
- public copy
- approved covers/media
- release or preorder mode
- target audience and call-to-action

Outputs:
- publication-facing site/app/static assets
- launch notes
- public metadata
- `projects/<project_id>/front-end/PROMOTION.yaml` — gate pending implementation

User gate:
- user approves copy, media, public state, and launch path before final
  packaging or publication.

## Local Skills

No local skills yet. Use `machinery/AGENTS.md` for Studio frontend
work; Studio is machinery, not this stage.

## Tools

- Project-specific build tools kept under `projects/<project_id>/front-end/`.

Publication front-end files belong under `projects/<project_id>/front-end/`,
which is local-only and ignored by Git.
