# AGENTS.md — Root Dispatcher

Read this file first. Then read `ONTOLOGY.md` for full repo detail, or read the
relevant stage `AGENTS.md` for the task at hand.

---

## Phase 0: Classify

Before routing, determine the job type. Every request is one of four types:

| Job type | Signals | Produces |
|---|---|---|
| `pipeline/<stage>` | Changes or produces an artifact under `projects/<id>/` | Stage output + PROMOTION.yaml |
| `research` | Finding, evaluating, or deciding on sources — not yet committing them | Research note (optional) |
| `conversation` | Question, planning discussion, feedback — no artifact target | Answer or decision |
| `tooling` | Change to CLI, infrastructure, docs, or skills | Code or doc change |

**Classify first. Route second.**

If the job type is ambiguous, load `machinery/skills/task-classifier/SKILL.md`.

---

## Phase 1: Composite Paths

A single request can be a sequence of job types. Declare the full path before
starting; execute each phase in order; pause at each transition for user input.

| Path | When | Transition trigger |
|---|---|---|
| `pipeline/<stage>` | All inputs known — rote execution | — |
| `conversation → pipeline/<stage>` | Required inputs missing or ambiguous | User provides missing input |
| `research → pipeline/ingest` | Source not yet identified | User approves candidate |
| `research → conversation` | Research raises an unanswerable question | Question surfaced to user |
| `conversation` | Planning, scoping, feedback — no execution | — |
| `tooling` | Framework change only | User approves scope |
| `tooling → pipeline/<stage>` | Fix a tool, then use it in the same session | Tool change complete + user confirms |

**Rote vs. conversation-required** is a property of the task instance, not the type:
- Rote: all required inputs present → execute immediately
- Conversation-required: inputs missing or a decision is needed → ask first, then re-classify

---

## Phase 2: Route

### Pipeline routing

| Request involves | Stage | Read next |
|---|---|---|
| Finding, downloading, or registering sources | `ingest/` | `ingest/AGENTS.md` |
| Transcribing text from source scans | `transcribe/` | `transcribe/AGENTS.md` |
| Auditing, correcting, or writing editorial prose | `proof/` | `proof/AGENTS.md` |
| Building PDFs, managing poems, setting layout | `typeset/` | `typeset/AGENTS.md` |
| Cover assets or cover production | `covers/` | `covers/AGENTS.md` |
| E-reader, web, or publication-facing output | `front-end/` | `front-end/AGENTS.md` |
| Release packaging or delivery | `final/` | `final/AGENTS.md` |

For each routed stage: read stage `AGENTS.md`, load relevant skills, use only that
stage's tools, identify required user input, record outputs under
`projects/<project_id>/<stage>/`.

For requests spanning multiple pipeline stages, process in DAG order.

### Non-pipeline routing

| Job type | Read next | Notes |
|---|---|---|
| `conversation` | No additional file | Respond directly; no stage artifact |
| `research` | `ingest/AGENTS.md` for source context | Optionally persist findings as `<topic>.research.md` in `projects/<id>/ingest/` |
| `tooling` | `machinery/AGENTS.md` | |

---

## DAG

```
project-create → ingest → transcribe → proof → typeset → [covers, front-end] → final
                                        proof → final  (direct, for short-form work)
```

Each pipeline edge requires a user gate. Gate details live in the stage's `AGENTS.md`.

---

## Project Structure

```
projects/<project_id>/
  ingest/        ← raw sources, provenance records, PROMOTION.yaml
  transcribe/    ← transcription files, plans, metadata, PROMOTION.yaml
  proof/         ← audit reports, corrections, PROMOTION.yaml
  typeset/       ← collection.yaml, content/, output/, PROMOTION.yaml   ← build root
  covers/        ← cover assets and production files
  front-end/     ← publication-facing assets
  final/         ← release packages and manifests
```

`workspace.yaml` maps project IDs to typeset paths. See `ONTOLOGY.md §
workspace.yaml` for the schema.

---

## System Invariants

Three critical rules — see `ONTOLOGY.md § Key Invariants` for the full list:

- `section_id` is the directory name, not `_meta.yaml:id`.
- Stage agents write only to `projects/<id>/<stage>/`. Cross-stage writes
  require explicit user approval.
- Persona prose never enters source text, YAML, manifests, audits, or command
  output.

---

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

---

## Skills Update Loop

At the end of every significant task:

1. Identify which skills were loaded and which should have been loaded.
2. Note any friction, missing instruction, unclear boundary, or tool gap.
3. If the fix is obvious and low-risk, update the relevant `SKILL.md` now.
4. If the fix is speculative or broad, record it as a proposed follow-up.
5. Never bake one-off task results into reusable skills.

Use `machinery/skills/skill-improvement-loop/SKILL.md` for full guidance.

---

## Full Reference

For directory taxonomy, file schemas, command surface, dependency map, and
all invariants: read `ONTOLOGY.md`.
