# Texgraph

A Markdown → LuaLaTeX → PDF/X pipeline for typesetting scholarly poetry editions.
Hand-curated poems (one Markdown file per poem) flow through a staged pipeline —
source acquisition, transcription, editorial manuscript, interior typesetting,
covers, publication, release — into print-ready books.

The CLI is `texgraph` (Python, `machinery/src/texgraph/`). Work is organized into
**projects** under `projects/`, each registered in `workspace.yaml`.

## What's here

| Project | What it is |
|---|---|
| `fletcher-early-works` | **Default.** Vol 1 of the Fletcher series — *The Early Works*, five 1913 books, 276 poems. Built: 534-page interior, print-ready PDF/X. |
| `fletcher-dominant-works` / `-embattled-works` / `-falling-works` | Vols 2–4 of the series. Scaffolds awaiting transcription → reading promotion. |
| `fletcher-series` | Shared, non-buildable series root: source PDFs (by era), `four_volume_order.md`, `PROJECT_PLAN.md`, series covers, `SERIES.md`. |
| `lift-wind-love-heat` | A standalone collection (not Fletcher). |
| `spectra_poems` | The tracked example project (*Iberian Dreams*) — a working build to model on. |

Quickstart and install: `machinery/docs/QUICKSTART.md`. Authoritative repo map
(schemas, full command surface, invariants): `machinery/docs/ONTOLOGY.md`.

## Repository layout

```
AGENTS.md                  root handoff (see below)
README.md                  this file
workspace.yaml             project registry (gitignored; example tracked)
machinery/
  src/texgraph/            all runtime Python + Jinja templates (the CLI)
  tools/                   maintenance scripts (ontology check, dataset, migrations)
  tests/                   pytest suite
  docs/                    canonical docs (ONTOLOGY, PROCEDURES, QUICKSTART, ...)
  skills/                  framework skills (task classifier, tooling, ...)
  studio/                  optional FastAPI + React review UI
modules/<module>/          per-stage contracts: AGENTS.md, RUNBOOK.md, schemas, skills (NO code)
projects/<id>/             a project's pipeline stages + its AGENTS.md
```

---

## Agent Framework

### Entry: one handoff, then close the loop in the project

`AGENTS.md` (root) does exactly one thing: identify the active project and hand
you to **`projects/<id>/AGENTS.md`**. That project file is self-contained for
routine work — identity, the commands it uses, its working conventions, and its
current pipeline gate. You should not need to traverse module docs to do ordinary
project work; the routing loop ends at the project.

```
root AGENTS.md ──▶ projects/<id>/AGENTS.md ──▶ (do the work)
```

Leave the project only for **framework or cross-project work** — the CLI, the
module pipeline, skills, schemas, repo structure. That machinery is *described*
below and in `machinery/docs/ONTOLOGY.md`; it is reference, not a routing maze.

Two loops always apply (kept in root `AGENTS.md`): the **ontology update loop**
(`machinery/tools/ontology_check.py` after structural/CLI/schema/edge changes) and
the **skills update loop** (patch `SKILL.md` gaps after significant work).

### The pipeline (described, not live-routed)

Each project moves through a DAG of stages; each edge is a user-approved gate
recorded in a `PROMOTION.yaml`:

```
workspace → sources → transcription → manuscript → interior → [covers, publication] → release
```

| Stage (`modules/<m>/`) | Owns | Project artifacts |
|---|---|---|
| `workspace` | project registration | `workspace.yaml` |
| `sources` | source acquisition, provenance, stable naming | `sources/` |
| `transcription` | poem-per-file transcription from scans | `transcription/` |
| `manuscript` | editorial reading edition, proofing, corrections | `manuscript/reading/` |
| `interior` | typeset proofs and print-ready PDFs | `interior/` (output under `output/`) |
| `covers` · `publication` · `release` | cover production · e-book/web · packaging | `covers/` · `publication/` · `release/` |

Each `modules/<m>/AGENTS.md` is a thin contract (scope + artifact boundary);
`modules/<m>/RUNBOOK.md` holds operating steps for `sources`, `transcription`,
`interior`, `manuscript`. **Skills** (`modules/<m>/skills/*/SKILL.md` and
`machinery/skills/*`) are loadable how-to guides — e.g. `interior/skills/typesetting`
(render_config, page modes, the measured one-poem-per-page layout, PDF/X),
`manuscript/skills/poetry-proof`, `transcription/skills/poem-transcription`.

### Command surface

| Command | Purpose |
|---|---|
| `build` | Render a collection to a full PDF (legacy non-poetry templates). |
| `proof-build [--config <sheet>] [--print-ready]` | The omnibus interior pipeline → review proof, trim variant, or even-page PDF/X. |
| `proof-preview [--pages] [--sample]` | Render structural pages to PNG for visual review (needs poppler). |
| `verify-coverage` | Prove every transcription poem maps 1:1 to a built reading poem. |
| `watch` · `list` · `new poem` | Auto-rebuild · list projects · scaffold a poem. |
| `verify <stage>` · `promote <stage>` | Check / approve a pipeline gate (`PROMOTION.yaml`). |
| `migrate modules` · `modules list/verify` | Module-layout migration and registry. |
| `audit` · `metadata` · `scan` · `plan` · `page-map` | Transcription audit, `book.json`, source scanning, plan/page mapping. |
| `pdf info/text/render` · `archive files/download` · `studio` | PDF inspection · Internet Archive · review UI. |

Full flags and schemas: `machinery/docs/ONTOLOGY.md § Command Surface`.

---

## Repository Audit — 2026-06-18

A full read-only audit (code, tooling, agent framework, project structure) was
run after the Fletcher four-volume split. The framework reformulation above
addresses the routing findings. Remaining items, by priority:

### Fixed in this pass
- **Root routing reformulated** — root `AGENTS.md` now hands off to per-project
  `AGENTS.md` (created for all six workspace projects); the 4× duplicated
  routing/classification/DAG tables are replaced by this one described framework.
- **Stale agent-framework refs** — `modules/manuscript/RUNBOOK.md` header and its
  pointer to the removed `typeset/AGENTS.md`; dangling deprecated-stage references
  (`transcribe/AGENTS.md`, `proof/AGENTS.md`) in skill "Required Reads".
- **Broken one-shot tools** repaired or retired (`add_source_field.py`,
  `strip_note_prefix.py`, `scaffold_typeset_poems.py` hard-coded the pre-split
  project path).
- **Studio UI path bug** — `CoverStudio.tsx` showed a dead, doubled
  `projects/.../projects/fletcher-complete-original-collections/...` path.
- **`workspace.example.yaml`** updated to model multi-project (series) registration.

### Recommended (not yet done — larger or judgement calls)
| Pri | Finding | Location |
|---|---|---|
| High | **Dead argparse CLI layer** duplicated by the live Typer CLI: `pdf.py` and `archive.py` are entirely dead; `register()`/`_run()` pairs in `audit/scan/metadata/plan/pagemap` are orphaned. Remove them and have `cli.py` call the pure functions. | `machinery/src/texgraph/` |
| Med | **Unused templates/method** — `base_preamble`, `frontmatter`, `section_title`, `pdfx_metadata` Jinja templates and `renderer.render_poem()`/`poem.tex.jinja2` have no caller. | `templates/`, `renderer.py` |
| Med | **`HANDOFF.md` describes the pre-split repo** (obsolete single project, dead `RUN_REPORT.md` path). Update or fold into this README. | `machinery/docs/HANDOFF.md` |
| Med | **Tests bound to live Fletcher data** (coverage + proof-build path tests). Prefer fixtures. Untested: `cli`, `compiler._parse_log`, `config`, `workspace`, `env` guard, renderer cycle/screenplay/prose paths. | `machinery/tests/` |
| Low | **Legacy stage aliases** (`ingest/transcribe/typeset/proof/final`) remain live for back-compat; retire once no project needs them. `studio`/`platform` modules are empty stubs — mark planned or remove. | `modules.py`, `promotions.py`, `modules/` |

Dated history docs (`MODULE_REFACTOR_STATUS.md`, `REPO_STRUCTURE_PLAN.md`) are
kept as records, not live guidance.
