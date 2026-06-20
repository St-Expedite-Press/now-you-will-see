---
name: repo-maintenance
description: "Maintain the modular publishing framework. Use when adding folders, scaffolding projects, updating documentation or metadata, standardizing filenames, editing AGENTS.md, coordinating DAG module contracts, updating docs, or syncing project metadata."
module: machinery
tools:
  - texgraph modules list
  - texgraph migrate modules
---
# Repo Maintenance

## Repository Shape

Keep the framework organized around:

- `README.md` — comprehensive repo reference: directory taxonomy, schemas, commands, invariants
- `README.md` — documentation index
- `README.md` — full project overview
- `AGENTS.md` — root dispatcher: routing table, DAG, loops
- `modules/<module>/AGENTS.md` — module contract: inputs, outputs, gate, skills, tools
- `modules/<module>/skills/<name>/SKILL.md` — reusable workflow programs, loaded on demand
- `modules/<module>/tools/` — deterministic helpers owned by a module
- `machinery/skills/` — cross-module infrastructure workflow programs
- `tools/` — cross-module infrastructure scripts
- `projects/<project_id>/` — local full-module project body (gitignored except tracked examples)
- `framework/PERSONA.md` — editorial voice contract template for generative prose
- root `README.md` — the comprehensive doc and authoritative repo map; `CLAUDE.md` — session-protocol pointer into it; `AGENTS.md` — root dispatcher

## Rules

1. Prefer existing naming and metadata patterns.
2. Keep unrelated edits out of the change.
3. Do not mark a module complete before required user inputs are satisfied.
4. When directory structure, schemas, CLI commands, or pipeline edges change:
   run `tools/ontology_check.py` and update `README.md` before committing.
5. Keep `AGENTS.md` lean — routing table and loops only. Detail lives in `README.md`.
6. Keep persona instructions in `framework/PERSONA.md`; do not duplicate them in plans or metadata.
7. Keep tool instructions in `machinery/skills/tooling/SKILL.md` and module `AGENTS.md` files.
8. For new tools, document the command name, inputs, outputs, user gate, and
   verification path before implementation. Use `README.md`.
9. Treat empty project module folders as valid placeholders.
10. After any significant repo change, run the ontology checker and save a new baseline
    when `README.md` has been updated. See `machinery/skills/technical-docs/SKILL.md`.
