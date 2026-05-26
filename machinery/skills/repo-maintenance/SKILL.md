---
name: repo-maintenance
description: Maintain the staged publishing framework. Use when adding folders, scaffolding projects, updating README or metadata, standardizing filenames, editing AGENTS.md, coordinating DAG stage contracts, updating docs, or syncing project metadata.
---

# Repo Maintenance

## Repository Shape

Keep the framework organized around:

- `ONTOLOGY.md` — comprehensive repo reference: directory taxonomy, schemas, commands, invariants
- `AGENTS.md` — root dispatcher: routing table, DAG, loops
- `<stage>/AGENTS.md` — stage contract: inputs, outputs, gate, skills, tools
- `<stage>/skills/<name>/SKILL.md` — reusable workflow programs, loaded on demand
- `<stage>/tools/` — deterministic helpers owned by a stage
- `machinery/skills/` — cross-stage infrastructure workflow programs
- `machinery/tools/` — cross-stage infrastructure scripts
- `projects/<project_id>/` — local full-stage project body (gitignored except tracked examples)
- `PERSONA.md` — editorial voice contract template for generative prose

## Rules

1. Prefer existing naming and metadata patterns.
2. Keep unrelated edits out of the change.
3. Do not mark a stage complete before required user inputs are satisfied.
4. When directory structure, schemas, CLI commands, or pipeline edges change:
   run `machinery/tools/ontology_check.py` and update `ONTOLOGY.md` before committing.
5. Keep `AGENTS.md` lean — routing table and loops only. Detail lives in `ONTOLOGY.md`.
6. Keep persona instructions in `PERSONA.md`; do not duplicate them in plans or metadata.
7. Keep tool instructions in `machinery/skills/tooling/SKILL.md` and stage `AGENTS.md` files.
8. For new tools, document the command name, inputs, outputs, user gate, and
   verification path before implementation. Use `machinery/docs/TOOL_PROPOSALS.md`.
9. Treat empty project stage folders as valid placeholders.
10. After any significant repo change, run the ontology checker and save a new baseline
    when `ONTOLOGY.md` has been updated. See `machinery/skills/technical-docs/SKILL.md`.

