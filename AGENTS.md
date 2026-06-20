# AGENTS.md — Root Handoff

Read this file first. It does one thing: hand you off to the project you are
working in. Routine work closes there — you should not need to hop through
module docs to do it.

## Handoff

1. **Identify the active project.** Use the `--project <id>` given to you; else
   the `workspace.yaml` `default_project` (currently `fletcher-early-works`); if
   neither is clear, ask which project before doing project work.
2. **Read `projects/<id>/AGENTS.md` and work from it.** It is self-contained for
   that project: identity, the commands it actually uses, its working
   conventions, and its current pipeline gate. The routing loop ends there.
3. **Only leave the project for framework or cross-project work** — changes to
   the CLI, the module pipeline, skills, schemas, or the repo structure. For
   that, see **`README.md`** — the comprehensive repo doc and authoritative map
   (modules, the DAG, skills, schemas, command surface, invariants).

**Load context by relevance.** Whatever you route to, pull in only the skills and
tools the task's module needs — see `README.md § Skill & Tool
Loading Contract` and its Skill & Tool Index (classify → match the module row →
open only that `SKILL.md`, use only its tools). Do not preload other modules'
docs/skills or the full command surface; a `conversation` task loads neither.

If a project has no `AGENTS.md` yet, model a new one on
`projects/fletcher-early-works/AGENTS.md`.

## Two loops that always apply

- **Ontology update** — after any task that changes directory structure, file
  formats, CLI commands, data schemas, or pipeline edges, run
  `python tools/ontology_check.py`; update `README.md`
  where flagged, then `--save-baseline`.
- **Skills update** — after any significant task, review which `SKILL.md` files
  were (or should have been) loaded and patch obvious, low-risk gaps. Never bake
  one-off task results into a reusable skill. Guidance:
  `machinery/skills/skill-improvement-loop/SKILL.md`. If you add or edit a skill,
  keep its frontmatter (`name`, `description`, `module`, `tools`) complete and run
  `python tools/skill_index.py --write` so the Skill & Tool Index and the
  `--check` gate stay green.

## Non-negotiable invariants

Full list in `README.md § Key Invariants`. The ones you can
break without noticing:

- Hand-curated text never lives under a directory a build writes. Reading
  editions live in `manuscript/reading/`; builds consume them read-only and
  write only under `interior/output/`.
- A module/stage writes only to its own artifact directory; cross-module writes
  need explicit user approval.
- Persona/editorial voice never enters source text, YAML, manifests, audits, or
  command output.
- `modules/<module>/` holds contracts only (AGENTS.md, RUNBOOK.md, schemas,
  skills) — never runtime code. All Python lives in `machinery/src/texgraph/`;
  all canonical docs in `README.md`.
