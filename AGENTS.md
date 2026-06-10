# AGENTS.md — Root Dispatcher

Read this file first. Then read `machinery/docs/ONTOLOGY.md` for full repo
detail, or read the relevant module `AGENTS.md` for the task at hand.

---

## Phase 0: Classify

Before routing, determine the job type. Every request is one of four types:

| Job type | Signals | Produces |
|---|---|---|
| `pipeline/<module>` | Changes or produces an artifact under `projects/<id>/` | Module output + PROMOTION.yaml |
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
| `pipeline/<module>` | All inputs known — rote execution | — |
| `conversation → pipeline/<module>` | Required inputs missing or ambiguous | User provides missing input |
| `research → pipeline/sources` | Source not yet identified | User approves candidate |
| `research → conversation` | Research raises an unanswerable question | Question surfaced to user |
| `conversation` | Planning, scoping, feedback — no execution | — |
| `tooling` | Framework change only | User approves scope |
| `tooling → pipeline/<module>` | Fix a tool, then use it in the same session | Tool change complete + user confirms |

**Rote vs. conversation-required** is a property of the task instance, not the type:
- Rote: all required inputs present → execute immediately
- Conversation-required: inputs missing or a decision is needed → ask first, then re-classify

---

## Phase 2: Route

### Pipeline routing

| Request involves | Module | Read next |
|---|---|---|
| Workspace registration and project creation | `workspace` | `modules/workspace/AGENTS.md` |
| Finding, downloading, or registering sources | `sources` | `modules/sources/AGENTS.md` |
| Transcribing text from source scans | `transcription` | `modules/transcription/AGENTS.md` |
| Auditing, correcting, or editorial review | `manuscript` | `modules/manuscript/AGENTS.md` |
| Building proof drafts, PDFs, poems, and layout | `interior` | `modules/interior/AGENTS.md` |
| Cover assets or cover production | `covers` | `modules/covers/AGENTS.md` |
| E-reader, web, or publication-facing output | `publication` | `modules/publication/AGENTS.md` |
| Release packaging or delivery | `release` | `modules/release/AGENTS.md` |

For each routed module: read module `AGENTS.md`, load relevant skills, use only
that module's tools, identify required user input, and record outputs under the
module-owned project artifact directory.

For requests spanning multiple pipeline modules, process in DAG order.

### Non-pipeline routing

| Job type | Read next | Notes |
|---|---|---|
| `conversation` | No additional file | Respond directly; no stage artifact |
| `research` | `modules/sources/AGENTS.md` for source context | Optionally persist findings as `<topic>.research.md` in `projects/<id>/sources/` |
| `tooling` | `machinery/AGENTS.md` | |

---

## DAG

```
workspace → sources → transcription → manuscript → interior → [covers, publication] → release
```

Each pipeline edge requires a user gate. Gate details live in the module's `AGENTS.md`.

---

## Project Structure

```
projects/<project_id>/
  sources/        ← raw sources, provenance records, PROMOTION.yaml
  transcription/  ← transcription files, plans, metadata, PROMOTION.yaml
  manuscript/     ← proofing, corrections, textual review
  interior/       ← collection.yaml, content/, proof drafts, output/, PROMOTION.yaml
  covers/         ← cover assets and production files
  publication/    ← publication-facing assets
  release/        ← release packages and manifests
```

All registered projects use the canonical module directories (migrated
2026-06-10). The reading edition lives in `manuscript/reading/`; builds
consume it read-only and write only under `interior/output/`. For any
project restored from an old layout, run
`texgraph migrate modules --project <id> --dry-run` first.

`workspace.yaml` maps project IDs to their interior roots
(`projects/<id>/interior`).

---

## System Invariants

Critical rules — see `machinery/docs/ONTOLOGY.md § Key Invariants` for the full list:

- `section_id` is the directory name, not `_meta.yaml:id`.
- Module agents write only to their module-owned artifact directory.
  Cross-module writes require explicit user approval.
- Persona prose never enters source text, YAML, manifests, audits, or command
  output.
- Hand-curated text never lives under a directory any build writes. Reading
  editions live in `manuscript/`; builds consume them read-only and write
  only under `interior/output/`.
- One doc home (`machinery/docs/`), one Python import root
  (`machinery/src/texgraph/`), and `modules/<module>/` holds contracts only
  (AGENTS.md, module.yaml, RUNBOOK.md, schemas, skills) — no runtime code.

---

## Ontology Update Loop

After any task that changes directory structure, file formats, CLI commands,
data schemas, or pipeline edges — run:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

If it flags changes in tracked areas, update `machinery/docs/ONTOLOGY.md`
before closing.
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
all invariants: read `machinery/docs/ONTOLOGY.md`.
