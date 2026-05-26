---
name: repo-maintenance
description: Maintain the staged publishing framework. Use when adding folders, scaffolding projects, updating README or metadata, standardizing filenames, editing AGENTS.md, coordinating DAG stage contracts, updating docs, or syncing project metadata.
---

# Repo Maintenance

## Repository Shape

Keep the framework organized around:

- `AGENTS.md` as the canonical root ontology, DAG contract, and dispatcher
- `machinery/docs/DAG_PIPELINE.md` for stage graph and promotion rules
- `machinery/docs/STUDIO_MODULES.md` for future frontend module-agent contracts
- `machinery/docs/TOOL_PROPOSALS.md` for proposed deterministic tools
- `projects/<project_id>/` as the local full-stage project body
- `<stage>/skills/` for stage-owned reusable workflows
- `<stage>/tools/` for deterministic helpers owned by a stage
- `machinery/skills/` for repository-maintenance and cross-stage infrastructure workflows
- `machinery/tools/` only for cross-stage infrastructure helpers
- `PERSONA.md` as the example persona contract for generative and editorial work

## Rules

1. Prefer existing naming and metadata patterns.
2. Keep unrelated edits out of the change.
3. Do not mark a stage complete before required user inputs are satisfied.
4. Update DAG and module docs when stage inputs, outputs, gates, or edges change.
5. Keep `AGENTS.md` as the canonical routing guide for repo-local skills.
6. Keep persona instructions in `PERSONA.md`; do not duplicate the whole
   persona inside plans or metadata.
7. Keep tool instructions in `machinery/skills/tooling/SKILL.md` and the owning stage `AGENTS.md`.
8. Keep frontend module requirements in docs until the user explicitly approves
   scaffolding or implementation.
9. For new tools, document the command name, inputs, outputs, user gate, and
   verification path before implementation.
10. Treat empty project stage folders as valid placeholders.

