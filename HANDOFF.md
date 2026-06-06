# Handoff Document

Read this file before reading anything else. It describes the current state of
the project, what has been built, what is pending, and what constraints must be
respected.

After reading this file, read `CLAUDE.md` for session startup protocol, then
`ONTOLOGY.md` for the full repo reference, then `AGENTS.md` for routing.

---

## What Texgraph Is

A staged publishing pipeline for serious literary production. Takes a poetry or
prose collection from raw source material through transcription, proof, and
typesetting to production-grade PDF/X-3 print files. The same Markdown/YAML
source targets multiple geometries (trade paperback, A5, chapbook, e-reader)
without re-authoring content. EPUB output is the intended next render target.

The system is AI-assisted but not AI-driven. The AI orchestrates and executes
within stage contracts; the user approves every promotion between stages.

---

## Architecture

### Three-Layer Context System

```
CLAUDE.md            ← session startup: mandatory loops, key commands, invariants
      │
ONTOLOGY.md          ← comprehensive map: directory taxonomy, schemas, commands
      │
AGENTS.md (root)     ← classify job type → route to stage
      │
<stage>/AGENTS.md    ← lean stage contract: inputs, outputs, gate, skills, tools
      │
<stage>/RUNBOOK.md   ← operator guide: concrete steps, paths, failure modes
      │
<skill>/SKILL.md     ← on-demand workflow programs, loaded when task matches
```

### Job Classification

Every request is classified before routing. Four types:

| Type | Signals | Produces |
|---|---|---|
| `pipeline/<stage>` | Artifact-producing work under `projects/<id>/` | Stage output + PROMOTION.yaml |
| `research` | Finding/evaluating sources without committing them | Research note (optional) |
| `conversation` | Question, planning, feedback — no artifact target | Answer or decision |
| `tooling` | CLI, infra, docs, or skill changes | Code or doc change |

Tasks can be composite sequences. Load `machinery/skills/task-classifier/SKILL.md`
when classification is ambiguous.

### Pipeline Gates

Each stage gate is enforced by `projects/<id>/<stage>/PROMOTION.yaml`.
`texgraph verify <stage>` reads the upstream gate and exits 1 with issues if
preconditions are unmet.

Implemented upstream gates (`machinery/src/texgraph/promotions.py`):

```python
UPSTREAM = {
    "transcribe": "ingest",
    "proof":      "transcribe",
    "typeset":    "proof",
    "final":      "typeset",
    "covers":     "final",   # requires cover_unlock.unlocked: true
}
```

`texgraph ingest rename` writes ingest PROMOTION.yaml with `status: pending`.
`texgraph promote <stage>` (not yet implemented) will write `status: approved`.
Until promote exists, users edit PROMOTION.yaml manually.

### DAG

```
project-create → ingest → transcribe → proof → typeset → [covers, front-end] → final
                                        proof → final  (direct, for short-form work)
```

---

## Current State

**Technical completeness: 65/100** *(was 61/100)*

| Axis | Score | Notes |
|---|---|---|
| Installability | 7/10 | QUICKSTART.md solid; requires TeX Live 4GB + font install |
| Core functionality | 7/10 | Build pipeline end-to-end works |
| Documentation | 9/10 | CLAUDE.md + 3 runbooks + transcription plans added; 4 runbooks still missing |
| Test coverage | 3/10 | 26 tests (audit, audit orchestrator, models, pagemap); promotions.py untested — biggest gap |
| CLI ergonomics | 6/10 | Good structure; missing `texgraph promote`; watch defaults draft=True vs build draft=False asymmetry |
| Architectural clarity | 9/10 | Stage isolation, classification, gates, hooks all coherent and documented |
| Pipeline completeness | 5/10 | Typeset done; covers/front-end/final are stubs; Vol 1 transcribed but not gated |
| AI/agent workflow | 9/10 | CLAUDE.md + hooks + 18 skills + runbooks + classification-first routing |
| Error handling | 5/10 | verify exits cleanly; gaps elsewhere; pdf text Windows encoding bug patched |
| Production readiness | 4/10 | Typeset output is vendor-quality; rest incomplete |

**Value: 74/100** — Unchanged. Concept stronger than implementation. Intellectual
integrity (9/10) and architectural clarity (9/10) are the strongest axes.

---

## What Is Built

### CLI (`texgraph`) — 18 commands across 4 sub-apps

| Command group | Commands |
|---|---|
| Build | `build`, `proof-build`, `watch`, `list`, `new poem`, `studio` |
| Pipeline gates | `verify <stage>`, `ingest rename` |
| PDF/source | `pdf info`, `pdf text`, `pdf render`, `archive files`, `archive download` |
| Editorial | `audit`, `metadata`, `page-map`, `plan`, `scan` |

### Python Package (`machinery/src/texgraph/`) — 17 modules

All `fletcher/` editorial tools merged flat into `texgraph/` in this session:
`env`, `models`, `audit`, `metadata`, `scan`, `pagemap`, `plan`, `pdf`, `archive`
merged alongside `cli`, `compiler`, `config`, `parser`, `promotions`, `renderer`,
`utils`, `workspace`.

### Gate infrastructure

`promotions.py` implements 5 stage checkers: ingest→transcribe, transcribe→proof,
proof→typeset, typeset→final, final→covers. Each checker validates
`PROMOTION.yaml` fields against on-disk state.

### Framework

- **19 skills** across 5 working stages (0 for covers, front-end, final)
- **3 runbooks** at stage roots: `ingest/RUNBOOK.md`, `transcribe/RUNBOOK.md`, `proof/RUNBOOK.md`
- **CLAUDE.md** — session startup, mandatory loops, key commands, invariants
- **`.claude/settings.json`** — PostToolUse hook (ontology check reminder on tracked file edits) + Stop hook (end-of-turn checklist)
- **ONTOLOGY.md** — updated with RUNBOOK.md and RUN_REPORT.md as documented file types
- **`projects/fletcher-complete-original-collections/RUN_REPORT.md`** — live session log

### Studio — FastAPI + React (50 frontend source files)

**Backend:** 11 API routers, 9 services. Implements project/section/poem CRUD,
versioning (`.{slug}.versions.yaml` sidecar system), render-config cascade
(global → section → poem), WebSocket build streaming, Claude agent chat, cover
asset gallery, and a read-only product readiness audit. Integrates directly with
the texgraph compiler pipeline.

**Frontend:** Five view modes. Cards view (poem browser + editor + properties
panel) fully functional. Build panel (live WebSocket log) fully functional.
Graph and covers views scaffolded but incomplete. Audit view now runs a read-only
product readiness audit and renders evidence, subagent scores, and final report.
Agent panel sends raw messages (not classification-aware). Zero PROMOTION.yaml
awareness anywhere in UI outside the audit findings.

### Projects

| Project | Stage | Poems | Status |
|---|---|---|---|
| `lift-wind-love-heat` | typeset (content complete) | 45+ | Buildable; no pipeline gating |
| `spectra_poems` | typeset (content complete) | 3 | Tracked example project; buildable |

---

## What Is Pending

Priority order, derived from audit:

### 1. `texgraph promote <stage>` — CLI gate step 5

The missing half of the gate system. `verify` checks preconditions; `promote`
writes `status: approved`. Without it, users edit PROMOTION.yaml manually.
Implementation: add `promote` command to `cli.py` + `promotions.py`. Show current
issues, ask for user confirmation, write `status: approved`.

### 2. Test coverage for gate infrastructure

`promotions.py`, `texgraph verify`, and `texgraph ingest rename` have zero tests.
`parser.py`, `renderer.py`, `compiler.py`, `config.py`, `workspace.py`,
`metadata.py`, `utils.py`, `archive.py` all untested. Only `audit.py`,
`models.py`, `pagemap.py`, and the audit orchestrator have tests (26 tests total).

Add: `test_promotions.py`, `test_cli_gates.py`, `test_parser.py`,
`test_metadata.py`. Use `tmp_path` fixtures; no real filesystem dependencies.

### 3. Gate PROMOTION.yaml for Fletcher Vol 1

276 poems transcribed across 5 books but `transcribe/PROMOTION.yaml` never
written. Run audit + metadata check, then write the file to unlock the proof stage.

### 4. Studio pipeline gate visibility

Zero PROMOTION.yaml awareness anywhere in the Studio frontend. Highest-value
UI addition: pipeline status panel showing each stage as locked/passing/blocked
with verify output inline. The graph view (DAG with live stage status) is the
natural home for this.

### 5. Fletcher Vol 2 architecture decision

`volumes/01_preludes-and-symphonies-1922/` created but orphaned from the official
`02_dominant_works/books/` structure. Decision required: dissolve into
`02_dominant_works/books/` (use 1915/1916 originals as copy-text) or keep as a
standalone edition-object volume (use 1922 Houghton Mifflin as copy-text).
The 1915/1916 originals are the correct copy-text for the critical edition.

### 6. Typeset RUNBOOK.md

`ingest/`, `transcribe/`, `proof/` all have complete runbooks. `typeset/`,
`covers/`, `front-end/`, `final/` do not. Typeset runbook is highest priority —
it covers the most common active workflow (building PDFs from existing content).

### 7. EPUB 3 renderer (`front-end/` stage)

Content model and parser already shared with typeset. Requires: Jinja2 XHTML
templates, OPF/NCX/container.xml generation, CSS for reflowable e-readers,
`texgraph epub --project <id>` CLI command, `front-end/skills/epub/SKILL.md`,
`texgraph verify front-end` gate in `promotions.py`. Estimated: 2–3 days.

### 8. Covers and final skills

Both stages have AGENTS.md contracts but no local skills. Covers needs at
minimum: trim-dependent bleed/safe-zone calculations and vendor format
requirements. Final needs: release checklist and delivery manifest schema.

### 9. Studio agent classification

AgentPanel sends raw messages. Should declare job type + composite path at
session start, following the root AGENTS.md model (classify → route → execute).

### 10. `mistune` dependency audit

`mistune` is listed in `pyproject.toml` dependencies but does not appear to
be used anywhere in the codebase. Remove or wire in.

### 11. `watch` draft-mode asymmetry

`watch` defaults `draft=True`; `build` defaults `draft=False`. This asymmetry
is confusing. Align to the same default or document the intent explicitly.

---

## Technical Constraints

Absolute. Violating these breaks things or creates security problems.

1. **Git author is CSandbatch only.** Never add Claude co-author lines to commits.
   No `Co-Authored-By` attribution of any kind.

2. **`.env` is never committed.** Contains live credentials. Gitignored. Never
   hardcode or echo these values.

3. **Stage isolation.** Write only to `projects/<id>/<stage>/`. Cross-stage writes
   require explicit user approval.

4. **No `<bucket>` in ingest paths.** Source files go directly in
   `projects/<id>/ingest/raw/<stable_name>.<ext>`.

5. **Persona prose boundary.** Editorial voice never enters source text, YAML
   manifests, audit output, or command output.

6. **PROMOTION.yaml `status: approved` requires user action.** Never write
   `status: approved` programmatically without user confirmation.

---

## Key Files

| File | Why to read it |
|---|---|
| `CLAUDE.md` | Session startup protocol — mandatory loops, key commands, invariants |
| `ONTOLOGY.md` | Complete repo map: directory taxonomy, all schemas, command surface, key invariants |
| `AGENTS.md` | Root dispatcher: classify → composite path → route. Read before any task. |
| `machinery/src/texgraph/promotions.py` | Gate implementation: UPSTREAM dict, verify_stage(), per-stage checkers |
| `machinery/src/texgraph/cli.py` | All CLI commands |
| `machinery/docs/DAG_PIPELINE.md` | Node contracts: implemented vs pending gates |
| `machinery/docs/STUDIO_FRONTEND.md` | Studio frontend routes, current status, development setup, and tests |
| `machinery/skills/task-classifier/SKILL.md` | Decision tree for ambiguous job type classification |
| `<stage>/AGENTS.md` | Stage contract: inputs, outputs, verify command, PROMOTION.yaml, tools |
| `<stage>/RUNBOOK.md` | Operator guide: concrete commands, example, failure modes |
| `projects/fletcher-complete-original-collections/RUN_REPORT.md` | Session log for active project |

---

## How to Start a Session

1. Read this file (done).
2. Read `CLAUDE.md` — session protocol and mandatory loops.
3. Read `AGENTS.md` — classify the incoming request.
4. If pipeline work: read the relevant stage `AGENTS.md` and `RUNBOOK.md`.
5. If repo-wide context needed: read `ONTOLOGY.md`.
6. If job type ambiguous: load `machinery/skills/task-classifier/SKILL.md`.
7. Check `projects/<id>/<stage>/PROMOTION.yaml`. Run `texgraph verify <stage>`.
8. Write only to `projects/<id>/<stage>/`. Record outputs there.
9. At end of task: run ontology checker if infrastructure changed; update
   skills if friction found; check PROMOTION.yaml if stage work is complete.

---

## Pending Work Checklist

### CLI
- [ ] `texgraph promote <stage>` — write approved PROMOTION.yaml
- [x] `texgraph proof-build` — proof PDF generation
- [ ] Fix `watch` draft-mode default to match `build`
- [ ] Remove or wire in `mistune` dependency

### Tests
- [ ] `test_promotions.py` — gate infrastructure tests
- [ ] `test_cli_gates.py` — verify/ingest rename integration tests
- [ ] `test_parser.py` — stanza splitting, cycle parsing, screenplay tests
- [ ] `test_metadata.py` — metadata generation, book.json validation

### Fletcher Edition
- [ ] Gate Vol 1 to proof: write `transcribe/PROMOTION.yaml`
- [ ] Decide on Vol 2 architecture: dissolve `01_preludes-and-symphonies-1922/` into `02_dominant_works/books/`
- [ ] Acquire Branches of Adam (Vol 3) source PDF
- [ ] Clarify Vol 4 rights and acquire sources (XXIV Elegies, South Star, The Burning Mountain)
- [ ] Transcribe Vol 2: begin with Symphonies (Goblins section II)

### Documentation
- [ ] `typeset/RUNBOOK.md` — most-needed missing runbook
- [ ] `covers/RUNBOOK.md`
- [ ] `front-end/RUNBOOK.md`
- [ ] `final/RUNBOOK.md`

### Skills
- [ ] Covers stage: at minimum one skill (bleed/safe-zone + vendor formats)
- [ ] Final stage: at minimum one skill (release checklist + delivery manifest)
- [ ] Front-end stage: `epub/SKILL.md` once EPUB renderer exists

### Studio
- [ ] Pipeline gate panel (PROMOTION.yaml status per stage)
- [ ] Graph view DAG (live stage status per node)
- [ ] Classification-aware agent (job type + composite path at session start)
- [x] Product readiness audit dashboard (read-only evidence + verdict)
- [ ] Promote flow UI (once CLI promote command exists)
- [ ] Action chips execution (programmatic change proposals)

### Pipeline completion
- [ ] EPUB 3 renderer (`texgraph epub`, front-end stage, verify gate)
- [ ] `texgraph verify front-end` gate in promotions.py
- [ ] Style token extraction (typeset → covers handshake)
- [ ] Cover payload reader
