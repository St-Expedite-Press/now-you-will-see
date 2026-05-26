# Handoff Document

This file exists for context continuity between AI sessions. Read it before
reading anything else. It describes the current state of the project, what has
been built, what is pending, and what constraints must be respected.

After reading this file, read `ONTOLOGY.md` for the full repo reference, then
`AGENTS.md` for routing and classification logic.

---

## What Texgraph Is

A staged publishing pipeline for serious literary production. It takes a poetry
or prose collection from raw source material through transcription, proof, and
typesetting to production-grade PDF/X-3 print files. The same Markdown/YAML
source can target multiple geometries (trade paperback, A5, chapbook, e-reader)
without re-authoring content. EPUB output is the intended next render target.

The system is AI-assisted but not AI-driven. The AI orchestrates and executes
within stage contracts; the user approves every promotion between stages.

---

## Architecture

### Three-Layer Context System

```
ONTOLOGY.md          ← comprehensive map: directory taxonomy, schemas, commands
      │
AGENTS.md (root)     ← classify job type → route to stage
      │
<stage>/AGENTS.md    ← lean stage contract: inputs, outputs, gate, skills, tools
      │
<skill>/SKILL.md     ← on-demand workflow programs, loaded when task matches
```

### Job Classification (root AGENTS.md)

Every request is classified before routing. Four types:

| Type | Signals | Produces |
|---|---|---|
| `pipeline/<stage>` | Artifact-producing work under `projects/<id>/` | Stage output + PROMOTION.yaml |
| `research` | Finding/evaluating sources without committing them | Research note (optional) |
| `conversation` | Question, planning, feedback — no artifact target | Answer or decision |
| `tooling` | CLI, infra, docs, or skill changes | Code or doc change |

Tasks can be composite sequences: `conversation → pipeline`, `research → pipeline/ingest`,
`tooling → pipeline`. Declare the path before starting. Load
`machinery/skills/task-classifier/SKILL.md` when classification is ambiguous.

### Pipeline Gates (PROMOTION.yaml)

Each stage gate is enforced by `projects/<id>/<stage>/PROMOTION.yaml`.
`texgraph verify <stage>` reads the upstream gate and exits 1 with issues if
preconditions are unmet.

Implemented upstream gates (from `machinery/src/texgraph/promotions.py`):

```python
UPSTREAM = {
    "transcribe": "ingest",
    "proof": "transcribe",
    "typeset": "proof",
    "final": "typeset",
    "covers": "final",   # requires cover_unlock.unlocked: true
}
```

`texgraph ingest rename` writes the ingest PROMOTION.yaml with `status: pending`.
`texgraph promote <stage>` (not yet implemented) will write `status: approved`.
Until promote exists, users edit PROMOTION.yaml manually to set status.

### DAG

```
project-create → ingest → transcribe → proof → typeset → [covers, front-end] → final
                                        proof → final  (direct, for short-form work)
```

### Stage Isolation

Stage agents write only to `projects/<id>/<stage>/`. Cross-stage writes require
explicit user approval. `projects/` is gitignored except tracked example projects.

---

## Current State

**Technical completeness: 61/100**

| Axis | Score | Notes |
|---|---|---|
| Installability | 7/10 | QUICKSTART.md solid; requires TeX Live 4GB + font install |
| Core functionality | 7/10 | Build pipeline end-to-end works |
| Documentation | 8/10 | All stage contracts updated; schemas in ONTOLOGY.md |
| Test coverage | 3/10 | 3 test files; gates untested — biggest gap |
| CLI ergonomics | 6/10 | Good structure; missing `texgraph promote` |
| Architectural clarity | 8/10 | Stage isolation, classification, gates all coherent |
| Pipeline completeness | 5/10 | Typeset done; covers/front-end/final are stubs |
| AI/agent workflow | 8/10 | Classification layer + PROMOTION.yaml + 18 skills |
| Error handling | 5/10 | verify exits cleanly; gaps elsewhere |
| Production readiness | 4/10 | Typeset output is vendor-quality; rest incomplete |

**Value: 74/100** — The concept is stronger than the implementation. Intellectual
integrity (9/10) and architectural clarity (8/10) are the strongest axes.
Addressable audience (5/10) is the ceiling: this is a niche tool for poets,
translators, and small press editors. That's appropriate — the high intellectual
integrity score is partly because it doesn't chase mass-market breadth.

---

## What Is Built

- **CLI** — `texgraph build`, `watch`, `list`, `new poem`, `studio`, `verify`, `ingest rename`,
  plus full editorial suite (`pdf`, `archive`, `audit`, `metadata`, `page-map`, `plan`, `scan`)
- **`promotions.py`** — PROMOTION.yaml I/O and per-stage precondition checkers for
  ingest, transcribe, proof, typeset, final, covers
- **Build pipeline** — Markdown/YAML → Jinja2 → LuaLaTeX → PDF/X-3, end-to-end
- **Job classification layer** — pipeline/research/conversation/tooling with composite
  paths, documented in `AGENTS.md` and `ONTOLOGY.md § Job Classification`
- **18 skills** across all active stages, organized by content type
- **Studio** — FastAPI backend + React/Vite/TypeScript frontend (47 source files):
  four editor views (cards, graph, build, covers), streaming hooks, Zustand stores,
  full API client layer
- **Example project** `spectra_poems` — tracked, buildable, three poems
- **Full documentation** — ONTOLOGY.md, AGENTS.md (classification-first), all stage
  AGENTS.md, QUICKSTART.md, DAG_PIPELINE.md, PROCEDURES.md, HANDOFF.md

---

## What Is Pending

Priority order:

### 1. `texgraph promote <stage>` (pipeline gate step 5)

The missing half of the gate system. `verify` checks preconditions; `promote`
writes `status: approved` to the PROMOTION.yaml. Without it, users must edit
PROMOTION.yaml manually. Implementation: add `promote` command to CLI, reads the
stage's PROMOTION.yaml, shows current issues, asks for user confirmation, writes
`status: approved`. Lives in `cli.py` + `promotions.py`.

### 2. Test coverage for gate infrastructure

`machinery/src/texgraph/promotions.py`, `texgraph verify`, and `texgraph ingest rename`
have zero tests. Add `machinery/tests/test_promotions.py` and
`machinery/tests/test_cli_gates.py`. Use tmp_path fixtures; no real filesystem
dependencies needed.

### 3. EPUB 3 renderer (`front-end/` pipeline stage)

The content model and parser are already shared with typeset. Adding EPUB means:
- Jinja2 XHTML templates for poem, prose, section, and collection document
- OPF/NCX/container.xml generation from `collection.yaml` metadata
- CSS for reflowable e-readers (stanza spacing, indentation, font fallback)
- `texgraph epub --project <id>` CLI command (or `--format epub` flag)
- `front-end/skills/epub/SKILL.md`
- `texgraph verify front-end` gate added to `promotions.py` UPSTREAM dict
Estimated effort: 2–3 focused days.

### 4. Studio pipeline gate visibility

The Studio frontend has no PROMOTION.yaml awareness. The highest-value UI addition:
a pipeline status panel showing each stage as locked/passing/blocked with the
verify output inline. Secondary: connect AgentPanel to the classify → route →
execute dispatch model so agent conversations declare their job type.
The graph view (DAG with live stage status) is the least complete Studio view.

### 5. `texgraph proof-build` (pipeline gate step 4)

Generate a proof PDF directly from the proof stage without requiring a full
typeset configuration. Lightweight PDF output for correction review.

### 6. covers/ and final/ skills

Both stages have AGENTS.md contracts but no skills. covers/ needs at minimum a
cover-spec skill describing trim-dependent bleed/safe-zone calculations and vendor
format requirements. final/ needs a release-checklist skill.

### 7. Style token extraction + cover payload (pipeline gate steps 6–7)

Typeset → covers handshake: extract typography/color tokens from the typeset
PROMOTION.yaml so covers can pick up the type regime without asking again.

---

## Front-End Needs (Detailed)

### Pipeline stage (`front-end/`)

The stage is a stub. Core need is the EPUB renderer described above. The
`front-end/AGENTS.md` has the contract; nothing else exists. No verify gate
is implemented for this stage (not in `promotions.py` UPSTREAM dict).

The content pipeline for EPUB mirrors typeset exactly:
`parser.py` → `renderer.py` (new EPUB branch) → EPUB packager → `.epub` file

No content model changes are needed. The same poem/prose Markdown, collection.yaml,
and section _meta.yaml files compile to EPUB as-is.

### Studio frontend (`machinery/studio/frontend/`)

47 source files. Router, four views, stores, API clients, streaming hooks — all
in place. Not a scaffold; an incomplete application.

Primary gaps:
1. **Pipeline gate panel** — No PROMOTION.yaml status anywhere in the UI. Add a
   stage progress indicator (possibly in TopBar or as a sidebar panel) showing
   verify status per stage with inline issue list on failure.
2. **Graph view** — `GraphCanvas` component exists but the DAG representation with
   live PROMOTION.yaml state per node is the least-built view. This is the natural
   home for pipeline status visualization.
3. **Classification-aware agent** — AgentPanel sends raw messages. Should declare
   job type + composite path at session start, following the root AGENTS.md model.
4. **Promote flow** — Once `texgraph promote` exists CLI-side, the Studio needs a
   "Approve & Promote" button that runs promote for the current stage.

---

## Technical Constraints

These are absolute. Violating them breaks things or creates security problems.

1. **Git author is CSandbatch only.** Never add Claude co-author lines to commits.
   No `Co-Authored-By` attribution of any kind.

2. **`.env` is never committed.** It contains live credentials (GitHub token, AWS,
   Stripe, OpenAI, HuggingFace). It is gitignored. Never hardcode or echo these values.

3. **Stage isolation.** Write only to `projects/<id>/<stage>/`. Cross-stage writes
   require explicit user approval. This is enforced by convention, not code — respect it.

4. **No `<bucket>` in ingest paths.** The bucket subdirectory was removed. Source
   files go directly in `projects/<id>/ingest/raw/<stable_name>.<ext>`.

5. **Persona prose boundary.** Editorial voice never enters source text, YAML
   manifests, audit output, or command output. The persona is for the edition
   wrapper; the transcription stays factual.

6. **PROMOTION.yaml `status: approved` requires user action.** Never write
   `status: approved` programmatically without user confirmation. The gate is the
   point.

---

## Key Files

| File | Why to read it |
|---|---|
| `ONTOLOGY.md` | Complete repo map: directory taxonomy, all schemas, command surface, key invariants |
| `AGENTS.md` | Root dispatcher: classify → composite path → route. Read before any task. |
| `machinery/src/texgraph/promotions.py` | Gate implementation: UPSTREAM dict, verify_stage(), per-stage checkers |
| `machinery/src/texgraph/cli.py` | All CLI commands including verify and ingest rename |
| `machinery/docs/DAG_PIPELINE.md` | Node contracts with implemented vs pending gates |
| `machinery/skills/task-classifier/SKILL.md` | Decision tree for ambiguous job type classification |
| `<stage>/AGENTS.md` | Stage contract: inputs, outputs, verify command, PROMOTION.yaml, tools |

---

## How to Start a Session

1. Read this file (done).
2. Read `AGENTS.md` — classify the incoming request.
3. If pipeline work: read the relevant stage `AGENTS.md`.
4. If repo-wide context needed: read `ONTOLOGY.md`.
5. If job type is ambiguous: load `machinery/skills/task-classifier/SKILL.md`.
6. Check `projects/<id>/<stage>/PROMOTION.yaml` before starting any stage work.
   Run `texgraph verify <stage>` to confirm the upstream gate is clear.
7. Write only to `projects/<id>/<stage>/`. Record outputs there.
8. At end of significant task: run ontology checker, update skills if needed.

---

## Pending Work Checklist (from README)

- [ ] `texgraph promote <stage>` — write approved PROMOTION.yaml
- [ ] `texgraph proof-build` — proof PDF generation
- [ ] Test coverage: `test_promotions.py`, `test_cli_gates.py`
- [ ] EPUB 3 renderer (`texgraph epub`)
- [ ] Studio pipeline gate visibility (PROMOTION.yaml status panel)
- [ ] Studio graph view (DAG with live stage status)
- [ ] Style token extraction (typeset → covers handshake)
- [ ] Cover payload reader
- [ ] covers/ skills and tools
- [ ] final/ skills and packaging
