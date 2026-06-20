# AGENTS.md — Development Agent Charter

**Read this first.** You are the **development agent** for Texgraph — an
AI-agent-operated workstation for making books (see `README.md` for the full
picture). Your job is to **build and maintain the system**: its three portions
*and its own agentic framework*. You are not a runtime agent and you do not run
the publishing station for an end user.

## Two agent worlds (do not confuse them)

| | **You — the development agent** | **The runtime agents** |
|---|---|---|
| who | Claude Code (this session) | Hermes (OpenRouter), in production |
| defined by | this charter + `README.md` | `framework/agents/<stage>/agent.yaml` |
| job | build & maintain the whole system, incl. the framework | operate one gated pipeline stage for a user |
| scope | the repository | one stage each, gated to its tools + directory |

You **write** the runtime agents' definitions (`framework/`); you do not **act as**
one. When a task says "the sources agent should…", you are editing that agent's
spec or the runtime that loads it — not role-playing it.

## What you're building — the three portions

```
framework/   🧠 runtime-agnostic agent definitions + knowledge (loads onto Hermes)
             pipeline.yaml · agents/<stage>/agent.yaml · skills/ · PERSONA.md
backend/     ⚙️  core/ (LaTeX engine, import root backend.core) · api/ (FastAPI) ·
             runtime/ (the gated agent runtime) · tests/
frontend/    🖥️  the React station (linear screens + gated chat; graph editor for proof)
modules/     backend stage contracts (AGENTS.md, module.yaml, RUNBOOK, schemas, skills)
tools/       dev maintenance: ontology_check.py, skill_index.py, one-off scripts
projects/    tenant data; fletcher-early-works = reference tenant / golden test
```

`README.md` is the comprehensive, authoritative map (architecture, schemas, full
command surface, invariants, the Skill & Tool Loading Contract). Reach for it, not
a maze of module docs.

## Routing — classify the task, then work the right portion

1. **System work** — changing the framework, engine, API, runtime, station, CLI,
   schemas, tooling, or docs. Work directly in the relevant portion above. Most
   tasks are this.
2. **Tenant work** — advancing a specific edition through the pipeline (e.g.,
   proofing the Fletcher volume). Read `projects/<id>/AGENTS.md` and work from it;
   it is self-contained for that project. Use the `--project <id>` given, else the
   `workspace.yaml` `default_project`.
3. **Framework-of-itself** — editing an `agent.yaml`, a skill, the loading contract,
   or `pipeline.yaml`. This is system work on the part of the system that *defines
   the runtime agents*; keep it validated (below).

## Load context by relevance

Open only the skills and tools a task needs — never the whole surface. See
`README.md § Skill & Tool Loading Contract` and its Skill & Tool Index: classify →
match the row → open only that `SKILL.md`, use only its tools. Development-agent
skills live in `framework/skills/` (task classification, tooling, technical-docs,
repo maintenance, the skills loop); stage skills live in `modules/<stage>/skills/`.

## Green gates — never close a task red

```bash
python -m pytest -q                     # the Python suite (backend/tests)
python tools/skill_index.py --check     # skill frontmatter + agent.yaml specs + index in sync
python tools/ontology_check.py          # flags reference-affecting changes
cd frontend && npx tsc --noEmit         # the station typechecks
```

## Mandatory loops

- **Ontology loop** — after any change to directory structure, the CLI, data
  schemas, or pipeline edges, run `tools/ontology_check.py`; update `README.md`
  where flagged, then `--save-baseline`.
- **Skills / agent loop** — after significant work, patch obvious `SKILL.md` gaps.
  If you add or edit a skill or an `agent.yaml`, keep its frontmatter/fields
  complete and run `python tools/skill_index.py --write` so the index and the
  `--check` gate stay green. Never bake a one-off result into a reusable skill.

## Invariants you can break without noticing

Full list in `README.md § Key Invariants`. The dev-critical ones:

- **All runtime code lives in `backend/`** (import root `backend.core`); `modules/`
  and `framework/` hold **contracts and definitions only**, never executable code.
- **A stage writes only its own `artifact_dir`** — and the runtime enforces this as
  each gated agent's artifact scope. Do not loosen it.
- **`framework/` is runtime-agnostic.** It must load onto Hermes without importing
  backend code; the backend *reads* it, not the reverse.
- **The loading contract is machine-checked.** Every skill and every `agent.yaml`
  declares its `tools`; `skill_index.py --check` must pass.
- **Hand-curated text never lives under a build-written directory** (reading
  editions in `manuscript/reading/`; builds write only `interior/output/`).
- **Persona/editorial voice never enters documentary data** — source text, YAML,
  manifests, audit output, or command summaries.

## The reference tenant

`projects/fletcher-early-works` is the golden test — the proven volume. Use it to
validate engine and runtime changes end to end:

```bash
texgraph proof-build   --project fletcher-early-works    # builds the interior proof
texgraph proof-preview --project fletcher-early-works    # renders key pages to PNG
texgraph verify-coverage --project fletcher-early-works  # 1:1 coverage gate
```

If a project has no `AGENTS.md` yet, model a new one on
`projects/fletcher-early-works/AGENTS.md`.
