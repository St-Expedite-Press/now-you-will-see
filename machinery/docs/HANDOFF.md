# Handoff Document

Read this file before reading anything else. It describes the current state of
the project, what has been built, what is pending, and what constraints must be
respected.

After reading this file, read `machinery/docs/CLAUDE.md` for session startup
protocol, then `machinery/docs/ONTOLOGY.md` for the full repo reference, then
root `AGENTS.md` for routing.

---

## What Texgraph Is

A staged publishing pipeline for serious literary production. Takes a poetry or
prose collection from raw source material through transcription, manuscript
preparation, and interior production to PDF/X-3 print files. The same Markdown/YAML
source targets multiple geometries (trade paperback, A5, chapbook, e-reader)
without re-authoring content. EPUB output is the intended next render target.

The system is AI-assisted but not AI-driven. The AI orchestrates and executes
within stage contracts; the user approves every promotion between stages.

---

## Architecture

### Three-Layer Context System

```
machinery/docs/CLAUDE.md
                     ← session startup: mandatory loops, key commands, invariants
      │
machinery/docs/ONTOLOGY.md
                     ← comprehensive map: directory taxonomy, schemas, commands
      │
AGENTS.md (root)     ← classify job type → route to stage
      │
modules/<module>/AGENTS.md
                      ← lean module contract: inputs, outputs, gate, skills, tools
      │
modules/<module>/RUNBOOK.md
                      ← operator guide when present
      │
<skill>/SKILL.md     ← on-demand workflow programs, loaded when task matches
```

### Job Classification

Every request is classified before routing. Four types:

| Type | Signals | Produces |
|---|---|---|
| `pipeline/<module>` | Artifact-producing work under `projects/<id>/` | Module output + PROMOTION.yaml |
| `research` | Finding/evaluating sources without committing them | Research note (optional) |
| `conversation` | Question, planning, feedback — no artifact target | Answer or decision |
| `tooling` | CLI, infra, docs, or skill changes | Code or doc change |

Tasks can be composite sequences. Load `machinery/skills/task-classifier/SKILL.md`
when classification is ambiguous.

### Pipeline Gates

Each module gate is enforced by `projects/<id>/<module>/PROMOTION.yaml`.
`texgraph verify <module>` reads the upstream gate and exits 1 with issues if
preconditions are unmet.

Canonical module order:

```text
workspace -> sources -> transcription -> manuscript -> interior -> [covers, publication] -> release
```

`texgraph ingest rename` writes sources PROMOTION.yaml with `status: pending`.
`texgraph promote <module>` (not yet implemented) will write `status: approved`.
Until promote exists, users edit PROMOTION.yaml manually.

### DAG

```
workspace → sources → transcription → manuscript → interior → [covers, publication] → release
```

---

## Current State

**Technical completeness: 70/100**

| Axis | Score | Notes |
|---|---|---|
| Installability | 7/10 | `machinery/docs/QUICKSTART.md` solid; requires TeX Live 4GB + font install |
| Core functionality | 7/10 | Build pipeline end-to-end works |
| Documentation | 8/10 | Canonical module docs now exist; legacy docs remain as redirects/compatibility notes |
| Test coverage | 4/10 | 38 tests; module registry, migration, promotions, and proof-build path contracts are covered |
| CLI ergonomics | 7/10 | Module list/verify/migrate added; missing `texgraph promote`; watch/build draft asymmetry remains |
| Architectural clarity | 9/10 | Module registry, aliases, DAG, and migration command are coherent and documented |
| Pipeline completeness | 5/10 | Interior build works; covers/publication/release remain partly skeletal |
| AI/agent workflow | 9/10 | Root dispatcher plus module AGENTS files support classification-first routing |
| Error handling | 5/10 | verify exits cleanly; gaps elsewhere; pdf text Windows encoding bug patched |
| Production readiness | 4/10 | Typeset output is vendor-quality; rest incomplete |

**Value: 74/100** — Unchanged. Concept stronger than implementation. Intellectual
integrity (9/10) and architectural clarity (9/10) are the strongest axes.

---

## What Is Built

### CLI (`texgraph`) — module-aware command surface

| Command group | Commands |
|---|---|
| Build | `build`, `proof-build`, `watch`, `list`, `new poem`, `studio` |
| Pipeline gates | `verify <module>`, `modules verify <module>`, `ingest rename` |
| Module registry/migration | `modules list`, `migrate modules --dry-run`, `migrate modules --apply` |
| PDF/source | `pdf info`, `pdf text`, `pdf render`, `archive files`, `archive download` |
| Editorial | `audit`, `metadata`, `page-map`, `plan`, `scan` |

### Python Package (`machinery/src/texgraph/`) — 17 modules

All `fletcher/` editorial tools merged flat into `texgraph/` in this session:
`env`, `models`, `audit`, `metadata`, `scan`, `pagemap`, `plan`, `pdf`, `archive`
merged alongside `cli`, `compiler`, `config`, `parser`, `promotions`, `renderer`,
`utils`, `workspace`.

### Module Registry and Gate Infrastructure

`machinery/src/texgraph/modules.py` is the shared module registry and migration
planner. `promotions.py` resolves canonical modules and compatibility aliases.
Aliases retained for one release cycle include `ingest`, `transcribe`, `proof`,
`typeset`, `front-end`, and `final`. Covers now unlock from approved `interior`,
not from `release`.

### Framework

- **Root `modules/` tree** with local `AGENTS.md`, `module.yaml`, `src/`,
  `tests/`, `skills/`, `schemas/`, and `tools/` folders per module
- **Legacy root stage docs** retained as compatibility redirects for one release cycle
- **`machinery/docs/CLAUDE.md`** — session startup, mandatory loops, key commands, invariants
- **`.claude/settings.json`** — PostToolUse hook (ontology check reminder on tracked file edits) + Stop hook (end-of-turn checklist)
- **`machinery/docs/ONTOLOGY.md`** — authoritative repo map, schemas, commands, and invariants
- **Root doc stubs** — `README.md`, `ONTOLOGY.md`, `HANDOFF.md`, `CLAUDE.md`,
  and `PERSONA.md` point to canonical files under `machinery/docs/`
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
| `lift-wind-love-heat` | interior legacy root (`typeset`) | 45+ | Buildable; not migrated |
| `spectra_poems` | interior legacy root (`typeset`) | 3 | Tracked example project; migration dry run passes |
| `fletcher-complete-original-collections` | legacy roots with module aliases | large active project | Migration dry run passes; not applied |

---

## What Is Pending

Priority order, derived from audit:

### 1. `texgraph promote <module>` — CLI gate step 5

The missing half of the gate system. `verify` checks preconditions; `promote`
writes `status: approved`. Without it, users edit PROMOTION.yaml manually.
Implementation: add `promote` command to `cli.py` + `promotions.py`. Show current
issues, ask for user confirmation, write `status: approved`.

### 2. Test coverage for gate infrastructure

Module registry, migration planning, promotion alias behavior, and proof-build
path contracts now have tests. Remaining gaps: `texgraph promote`, parser,
renderer, compiler, metadata, archive, and full CLI integration coverage.

Add: broader `test_cli_gates.py`, `test_parser.py`, `test_renderer.py`, and
`test_metadata.py`. Use `tmp_path` fixtures; no real filesystem dependencies.

### 3. Gate PROMOTION.yaml for Fletcher Vol 1

276 poems transcribed across 5 books but `transcribe/PROMOTION.yaml` never
written. Run audit + metadata check, then write the file to unlock manuscript/interior work.

### 4. Studio pipeline gate visibility

Studio now has module APIs and module status data. Highest-value UI addition:
make the graph view a canonical module DAG with locked/passing/blocked status
and verify output inline.

### 5. Fletcher Vol 2 architecture decision

`volumes/01_preludes-and-symphonies-1922/` created but orphaned from the official
`02_dominant_works/books/` structure. Decision required: dissolve into
`02_dominant_works/books/` (use 1915/1916 originals as copy-text) or keep as a
standalone edition-object volume (use 1922 Houghton Mifflin as copy-text).
The 1915/1916 originals are the correct copy-text for the critical edition.

### 6. Typeset RUNBOOK.md

Canonical module runbooks are still thin. `modules/interior/RUNBOOK.md` is the
highest priority because it covers the most common active workflow: proof and
production PDF builds from existing content.

### 7. EPUB 3 renderer (`publication` module)

Content model and parser already shared with typeset. Requires: Jinja2 XHTML
templates, OPF/NCX/container.xml generation, CSS for reflowable e-readers,
`texgraph epub --project <id>` CLI command,
`modules/publication/skills/epub/SKILL.md`, and a publication gate/checker.
Estimated: 2–3 days.

### 8. Covers and release skills

Both modules have AGENTS.md contracts but no mature local skills. Covers needs at
minimum: trim-dependent bleed/safe-zone calculations and vendor format
requirements. Release needs: release checklist and delivery manifest schema.

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

3. **Module isolation.** Write only to the active module artifact directory.
   Cross-module writes require explicit user approval.

4. **No `<bucket>` in sources paths.** Source files go directly in
   `projects/<id>/sources/raw/<stable_name>.<ext>` after migration. Legacy
   projects may retain `ingest/raw/`.

5. **Persona prose boundary.** Editorial voice never enters source text, YAML
   manifests, audit output, or command output.

6. **PROMOTION.yaml `status: approved` requires user action.** Never write
   `status: approved` programmatically without user confirmation.

---

## Key Files

| File | Why to read it |
|---|---|
| `machinery/docs/README.md` | Canonical documentation index |
| `machinery/docs/CLAUDE.md` | Session startup protocol — mandatory loops, key commands, invariants |
| `machinery/docs/ONTOLOGY.md` | Complete repo map: directory taxonomy, all schemas, command surface, key invariants |
| `machinery/docs/HANDOFF.md` | Current status, pending work, and session handoff |
| `AGENTS.md` | Root dispatcher: classify → composite path → route. Read before any task. |
| `machinery/src/texgraph/modules.py` | Canonical module registry, aliases, and project migration planner |
| `machinery/src/texgraph/promotions.py` | Gate implementation: module-aware verify_stage() and per-module checkers |
| `machinery/src/texgraph/cli.py` | All CLI commands |
| `machinery/docs/DAG_PIPELINE.md` | Node contracts: implemented vs pending gates |
| `machinery/docs/STUDIO_FRONTEND.md` | Studio frontend routes, current status, development setup, and tests |
| `machinery/skills/task-classifier/SKILL.md` | Decision tree for ambiguous job type classification |
| `modules/<module>/AGENTS.md` | Module contract: inputs, outputs, verify command, PROMOTION.yaml, tools |
| `modules/<module>/RUNBOOK.md` | Operator guide when present: concrete commands, example, failure modes |
| `projects/fletcher-complete-original-collections/RUN_REPORT.md` | Session log for active project |

---

## How to Start a Session

1. Read this file (done).
2. Read `machinery/docs/CLAUDE.md` — session protocol and mandatory loops.
3. Read `AGENTS.md` — classify the incoming request.
4. If pipeline work: read the relevant module `AGENTS.md` and `RUNBOOK.md` when present.
5. If repo-wide context needed: read `machinery/docs/ONTOLOGY.md`.
6. If job type ambiguous: load `machinery/skills/task-classifier/SKILL.md`.
7. Check `projects/<id>/<module>/PROMOTION.yaml`. Run `texgraph verify <module>`.
8. Write only to the active module artifact directory. Record outputs there.
9. At end of task: run ontology checker if infrastructure changed; update
   skills if friction found; check PROMOTION.yaml if stage work is complete.

---

## Pending Work Checklist

### CLI
- [ ] `texgraph promote <module>` — write approved PROMOTION.yaml
- [x] `texgraph proof-build` — proof PDF generation
- [ ] Fix `watch` draft-mode default to match `build`
- [ ] Remove or wire in `mistune` dependency

### Tests
- [x] `test_module_promotions.py` — module gate infrastructure tests
- [ ] `test_cli_gates.py` — verify/sources rename integration tests
- [ ] `test_parser.py` — stanza splitting, cycle parsing, screenplay tests
- [ ] `test_metadata.py` — metadata generation, book.json validation

### Fletcher Edition
- [ ] Gate Vol 1 to manuscript/interior: write `transcription/PROMOTION.yaml`
- [ ] Decide on Vol 2 architecture: dissolve `01_preludes-and-symphonies-1922/` into `02_dominant_works/books/`
- [ ] Acquire Branches of Adam (Vol 3) source PDF
- [ ] Clarify Vol 4 rights and acquire sources (XXIV Elegies, South Star, The Burning Mountain)
- [ ] Transcribe Vol 2: begin with Symphonies (Goblins section II)

### Documentation
- [ ] `modules/interior/RUNBOOK.md` — most-needed missing runbook
- [ ] `covers/RUNBOOK.md`
- [ ] `modules/publication/RUNBOOK.md`
- [ ] `modules/release/RUNBOOK.md`

### Skills
- [ ] Covers module: at minimum one skill (bleed/safe-zone + vendor formats)
- [ ] Release module: at minimum one skill (release checklist + delivery manifest)
- [ ] Publication module: `epub/SKILL.md` once EPUB renderer exists

### Studio
- [ ] Pipeline gate panel (PROMOTION.yaml status per stage)
- [ ] Graph view DAG (live stage status per node)
- [ ] Classification-aware agent (job type + composite path at session start)
- [x] Product readiness audit dashboard (read-only evidence + verdict)
- [ ] Promote flow UI (once CLI promote command exists)
- [ ] Action chips execution (programmatic change proposals)

### Pipeline completion
- [ ] EPUB 3 renderer (`texgraph epub`, publication module, verify gate)
- [ ] `texgraph verify publication` checker in promotions.py
- [ ] Style token extraction (interior → covers handshake)
- [ ] Cover payload reader
