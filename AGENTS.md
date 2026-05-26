# AGENTS.md — Root Dispatcher

Read this file first. Then read `ONTOLOGY.md` for full repo detail, or read the
relevant stage `AGENTS.md` for the task at hand.

## Prime Directive

Every request becomes one or more stage jobs. Assign each job to exactly one
stage. Do not collapse stages. Do not promote across a stage edge without the
required user input.

## Dispatch Rule

For every incoming request:

1. Classify the request using the routing table below.
2. Read that stage's `AGENTS.md`.
3. Load only the skill files relevant to the specific task.
4. Use only that stage's tools and commands.
5. Identify what user input is required before stage completion or promotion.
6. Record outputs under `projects/<project_id>/<stage>/`.

For requests spanning multiple stages, process in DAG order.

## Routing Table

| Request involves | Stage | Read next |
|---|---|---|
| Finding, downloading, or registering sources | `ingest/` | `ingest/AGENTS.md` |
| Transcribing text from source scans | `transcribe/` | `transcribe/AGENTS.md` |
| Auditing, correcting, or writing editorial prose | `proof/` | `proof/AGENTS.md` |
| Building PDFs, managing poems, setting layout | `typeset/` | `typeset/AGENTS.md` |
| Cover assets or cover production | `covers/` | `covers/AGENTS.md` |
| E-reader, web, or publication-facing output | `front-end/` | `front-end/AGENTS.md` |
| Release packaging or delivery | `final/` | `final/AGENTS.md` |
| CLI, Studio, tests, infrastructure, docs | `machinery/` | `machinery/AGENTS.md` |

## DAG

```
project-create → ingest → transcribe → proof → typeset → [covers, front-end] → final
                                        proof → final  (direct, for short-form work)
```

Each edge requires a user gate. Gate details live in the stage's `AGENTS.md`.

## Project Structure

```
projects/<project_id>/
  ingest/        ← raw sources, provenance records
  transcribe/    ← transcription files, plans, metadata
  proof/         ← audit reports, corrections
  typeset/       ← collection.yaml, content/, output/   ← build root
  covers/        ← cover assets and production files
  front-end/     ← publication-facing assets
  final/         ← release packages and manifests
```

`workspace.yaml` maps project IDs to typeset paths. See `ONTOLOGY.md §
workspace.yaml` for the schema.

## System Invariants

Three critical rules — see `ONTOLOGY.md § Key Invariants` for the full list:

- `section_id` is the directory name, not `_meta.yaml:id`.
- Stage agents write only to `projects/<id>/<stage>/`. Cross-stage writes
  require explicit user approval.
- Persona prose never enters source text, YAML, manifests, audits, or command
  output.

## Ontology Update Loop

After any task that changes directory structure, file formats, CLI commands,
data schemas, or pipeline edges — run:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

If it flags changes in tracked areas, update `ONTOLOGY.md` before closing.
Then save a new baseline:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```

## Skills Update Loop

At the end of every significant task:

1. Identify which skills were loaded and which should have been loaded.
2. Note any friction, missing instruction, unclear boundary, or tool gap.
3. If the fix is obvious and low-risk, update the relevant `SKILL.md` now.
4. If the fix is speculative or broad, record it as a proposed follow-up.
5. Never bake one-off task results into reusable skills.

Use `machinery/skills/skill-improvement-loop/SKILL.md` for full guidance.

## Full Reference

For directory taxonomy, file schemas, command surface, dependency map, and
all invariants: read `ONTOLOGY.md`.
