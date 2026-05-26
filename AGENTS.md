# AGENTS.md - Root Orchestrator And Project Ontology

This file is the canonical agent reference for the repository. Stage manuals
live in their own directories, but the root agent owns decomposition, routing,
project ontology, and promotion discipline.

## Prime Directive

Every request becomes one or more stage jobs. A stage job has:

- a stage directory
- required inputs
- user decisions or approvals
- expected outputs
- verification commands
- downstream edges in the project DAG

Do not collapse stages for convenience. Do not promote work across a stage edge
without the required user input.

## Dispatch Rule

For every request:

1. Decompose the request into stage jobs.
2. Assign each job to exactly one stage directory.
3. Read that stage's `AGENTS.md`.
4. Read only the needed local `skills/` files.
5. Use that stage's local `tools/` first.
6. Identify the user input required before stage completion or promotion.
7. Record outputs in the matching project stage directory.

For mixed requests, process stage jobs in DAG order.

## Stage DAG

The intended project flow is a directed acyclic graph, not a hidden linear
automation:

```text
project-create
  -> ingest
  -> transcribe
  -> proof
  -> typeset
  -> final

typeset -> covers -> final
typeset -> front-end -> final
proof   -> final
```

`final/` receives only user-approved artifacts from upstream stages. Future
automation may suggest transitions, but user decisions remain the promotion
gates.

## Stage Jobs

| Stage | Owns | Requires User Input |
| --- | --- | --- |
| `ingest/` | source acquisition, source naming, manifests, PDF intake | source selection, rights/provenance acceptance, naming approval |
| `transcribe/` | transcription, source matter, volume planning, project planning | target book/section, transcription policy choices, uncertain readings |
| `proof/` | verification, correction passes, editorial review | acceptance of corrections, unresolved textual questions, voice use |
| `typeset/` | build inputs, layout policy, interior production | trim, format, type regime, inclusion/exclusion decisions |
| `covers/` | cover assets, cover styles, cover production notes | visual direction, selected assets, vendor format, approval of cover proof |
| `front-end/` | publication-facing front-end deliverables | audience, copy, release mode, desired public surfaces |
| `final/` | release packaging, delivery manifests, print-ready handoff | final approval, vendor target, release checklist signoff |
| `machinery/` | CLIs, Studio app, tests, shared infrastructure, repo maintenance | implementation scope, compatibility break approval, tool behavior choices |

## Project Ontology

Projects use the same body plan:

```text
projects/<project_id>/
  ingest/
  transcribe/
  proof/
  typeset/
  final/
  covers/
  front-end/
```

Buildable project roots are `projects/<project_id>/typeset`.
`workspace.yaml` registers local project IDs and points each ID at its typeset
root. `workspace.example.yaml` is the public template.

## Agent Modules

The future Studio interface should treat each project module as an agent:

- Project Creation Agent
- Ingest Agent
- Transcribe Agent
- Proof Agent
- Typeset Agent
- Covers Agent
- Final Agent
- Front-End Agent
- Project Chat Agent

Each module-agent may read the entire project directory and consult an external
knowledge base when configured. Writes remain bounded to the active stage unless
the user approves a promotion or cross-stage edit.

External knowledge must be cited or recorded when it affects source facts,
rights, editorial decisions, or production choices. External knowledge never
overrides source evidence silently.

## Repository Layout

```text
AGENTS.md
PERSONA.md
workspace.example.yaml

ingest/AGENTS.md
ingest/skills/

transcribe/AGENTS.md
transcribe/skills/
transcribe/tools/

proof/AGENTS.md
proof/skills/

typeset/AGENTS.md
typeset/skills/

final/AGENTS.md
covers/AGENTS.md
front-end/AGENTS.md

machinery/AGENTS.md
machinery/src/
machinery/studio/
machinery/tests/
machinery/docs/
machinery/skills/
machinery/tools/
```

## Command Surfaces

The system currently exposes `texgraph` and `fletcher` as compatibility
entrypoints. They operate on one project DAG and one stage vocabulary.

- `texgraph`: build, project, DAG, and Studio commands.
- `fletcher`: source, editorial, metadata, and transcription commands.

Future tools should use shared project/stage language even when a command lives
under one of those entrypoints.

## Critical System Invariants

- `section_id` is the section directory name, not `_meta.yaml:id`.
- Shared helpers belong in `machinery/src/texgraph/utils.py`, not in
  `texgraph.cli`.
- Studio backend services resolve project paths through workspace/project
  services.
- Version sidecars use `.slug.versions.yaml`; canonical selection must match
  build behavior.

## Persona Boundary

Use `PERSONA.md` only for generative, editorial, structural, or institutional
prose. Keep literal transcription, YAML, manifests, audits, and command
summaries neutral.

## Repository Rules

- Keep reusable workflow instructions in the relevant stage `skills/` directory.
- Keep deterministic helper scripts in the relevant stage `tools/` directory.
- Keep cross-stage code, tests, Studio, and technical docs in `machinery/`.
- Update `machinery/docs/DAG_PIPELINE.md` when stage contracts or edges change.
- For repository-structure work, read `machinery/skills/repo-maintenance/SKILL.md`.
- Before final responses, review `machinery/skills/skill-improvement-loop/SKILL.md`.
