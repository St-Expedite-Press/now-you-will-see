# Repo Structure Plan

Date: 2026-06-10
Status: proposed — supersedes nothing; sequences and extends
`MODULE_REFACTOR_STATUS.md § Next Hardening Sequence`.

## Diagnosis

The repo is mid-migration between two organizing schemes and is paying for
both at once:

1. **Two routing systems.** Root stage dirs (`ingest/`, `transcribe/`,
   `proof/`, `typeset/`, `covers/`, `final/`, `front-end/`) each carry an
   `AGENTS.md`, while `modules/<module>/AGENTS.md` is the canonical
   dispatcher. Searches and new sessions find both.
2. **Two doc homes.** Root `README/ONTOLOGY/HANDOFF/CLAUDE/PERSONA` are
   "compatibility stubs" but are still full-sized files that drift from
   `machinery/docs/*` (both sides show as modified in git right now).
3. **Projects unmigrated.** Fletcher and Spectra still use legacy artifact
   dirs; `workspace.yaml` still accepts old `path` values.
4. **An ownership hole the migration doesn't cover.** The reading-edition
   editorial layer (three-section poem files, see
   `projects/fletcher.../typeset/EDITORIAL_PROCEDURE.md`) lives inside
   `typeset/content/`, which builds treat as regenerable output. A build
   wiped all 273 files once (2026-06-01). Hand-curated text is sitting in
   machine territory.
5. **Root clutter.** `logs/`, `output/`, stray `.env` variants,
   `requirements.txt` beside `pyproject.toml`, a `Makefile` nobody routes
   through, and unmanaged image dumps under project `covers/`.
6. **Session logs as a growing blob.** `projects/<id>/RUN_REPORT.md` is
   prepend-only and already multi-session.

## Target shape

```
Texgraph/
  AGENTS.md            <- root dispatcher (only routing file at root)
  CLAUDE.md            <- 3-line pointer (already is)
  README.md            <- short orientation + pointer to machinery/docs
  pyproject.toml, workspace.yaml, .env(.example), .gitignore
  machinery/           <- all runtime code, tools, tests, canonical docs
    src/texgraph/      <- the only Python import root
    studio/            <- the Studio app (backend + frontend)
    docs/              <- canonical documentation, single source of truth
    skills/  tools/  tests/
  modules/<module>/    <- CONTRACTS ONLY: AGENTS.md, module.yaml, RUNBOOK.md,
                          schemas/, skills/   (no src/, no tests/)
  projects/<id>/       <- semantic module artifact dirs:
    sources/  transcription/  manuscript/  interior/
    covers/  publication/  release/
    reports/           <- dated session reports; RUN_REPORT.md = index
  projects/_archive/
```

Gone from root: `ingest/ transcribe/ proof/ typeset/ covers/ final/
front-end/ logs/ output/` (after the redirect cycle below).

## Key decisions (recommended; flag disagreement before Phase 2)

- **D1 — modules/ holds contracts, not code.** Each module's `src/`,
  `tests/`, `tools/` stubs are removed; runtime code stays in
  `machinery/src/texgraph/` keyed by the registry (`modules.py`). One import
  root, one test suite. (Alternative — moving code into modules — doubles
  packaging surface for no current gain.)
- **D2 — the reading edition belongs to `manuscript/`.** The three-section
  editorial files move from `typeset/content/` to
  `projects/<id>/manuscript/reading/` during Fletcher's migration.
  `manuscript` is by charter "corrected manuscript, corrections, and textual
  review" — that is exactly what these files are. `interior` then *consumes*
  manuscript output read-only and never regenerates it. This closes the
  June 1 clobber class structurally, not by warning.
  `EDITORIAL_PROCEDURE.md` moves to `manuscript/` alongside it.
- **D3 — `modules/studio` and `modules/platform` are not pipeline modules.**
  Keep them as contracts for the app and shared infra, but mark them
  `kind: service` in `module.yaml` so DAG tooling and docs stop listing them
  beside pipeline stages.
- **D4 — one dated report per session.** `projects/<id>/reports/
  RUN-YYYY-MM-DD[-n].md`; `RUN_REPORT.md` becomes a one-line-per-session
  index. Existing blob is split once, mechanically.

## Phases

### Phase 0 — Freeze (half a day)
The working tree has ~40 modified + ~20 untracked files from the module
refactor. Nothing structural moves until this is committed.
1. Commit the in-flight refactor work as-is (one commit: code, one: docs).
2. `python machinery/tools/ontology_check.py --save-baseline` and commit the
   baseline. This is the "before" snapshot every later phase diffs against.

### Phase 1 — One doc home (1 session)
1. Shrink root `README.md`, `ONTOLOGY.md`, `HANDOFF.md`, `PERSONA.md` to
   ≤10-line pointers at `machinery/docs/<same name>` (CLAUDE.md already is).
   No content lives at root.
2. Delete `machinery/docs/QUICKSTART.md` duplication question by making the
   machinery copy canonical (root copy already deleted).
3. Add a "docs map" section to `machinery/docs/README.md`: every doc, one
   line, who reads it, when.
4. Gate: grep shows no operator instruction outside `machinery/docs/`,
   `modules/*/AGENTS.md`, project-local procedure files.

### Phase 2 — Close the CLI gaps that block migration (1–2 sessions)
1. `texgraph promote <module> --project <id>` (hardening item 1; gates stop
   being hand-edited YAML).
2. Teach the interior renderer the three-section manuscript format: typeset
   Editorial Relineation when present, else Original Lineation; Context
   Notes routed to apparatus or omitted by flag. Renderer reads from
   `manuscript/reading/` (D2) and writes only under `interior/output/`.
3. Extend `texgraph migrate modules` mapping to carry
   `typeset/content/ -> manuscript/reading/` and
   `proof/corrections/ -> manuscript/corrections/`.
4. Gate: pytest green; `modules verify` green for every module; a proof-build
   on a scratch copy never writes outside `interior/output/`.

### Phase 3 — Migrate projects (1 session each, in this order)
1. `spectra_poems` (low risk): `migrate modules --dry-run`, review, `--apply`,
   then build + proof-build, then commit.
2. `fletcher-complete-original-collections`: same, with D2 moves included.
   Verify: 277 reading files intact post-move (`grep -c '## Original
   Lineation'`), audit green, proof-build output diff reviewed.
3. `lift-wind-love-heat`: classify — migrate or move to `projects/_archive/`.
4. Update `workspace.yaml` entries to canonical `project_root` + module roots;
   drop legacy `path` acceptance at the end of this phase.

### Phase 4 — Remove the second routing system (1 session)
1. Replace each root stage dir's contents with a single `LEGACY.md` (5 lines:
   "moved to modules/<name>; artifacts under projects/<id>/<module>/").
2. One release cycle later (or immediately if no external consumers — they
   are all local agents): delete the root stage dirs and the alias layer in
   `modules.py`; `modules verify proof|typeset` aliases go with it.
3. Gate: `texgraph` test suite green with aliases removed; ontology_check
   diff reviewed and baseline re-saved.

### Phase 5 — Hygiene (1 session, mechanical)
1. Root `logs/` and `output/` → delete or relocate under `machinery/` /
   project dirs; gitignore both names at root.
2. `.env`, `.env.texgraph` → one `.env` (gitignored) + `.env.example`;
   document variables in DATA_DICTIONARY.
3. `requirements.txt` → fold into `pyproject.toml` extras; Makefile targets
   either documented in QUICKSTART or deleted.
4. Project `covers/`: adopt stable asset naming
   (`<project>_<volume>_<role>_<variant>.png`), move ChatGPT-named dumps and
   nested duplicate trees (`fletcher_four_volume_covers/fletcher_four_volume_covers`,
   `home/oai/share/...`) into `covers/_inbox/` pending rename-or-delete.
5. Split Fletcher `RUN_REPORT.md` into `reports/` per D4.

### Phase 6 — Lock it in (half a day)
1. `ontology_check.py` → update ONTOLOGY → `--save-baseline`.
2. Update `MODULE_REFACTOR_STATUS.md` to "complete"; record removals.
3. Update HANDOFF.md; add the structure rules to root AGENTS.md invariants:
   - hand-curated text never lives under a directory any build writes;
   - one doc home; one import root; contracts-only `modules/`.

## Effort and order of risk

Phases 0–1 are safe and immediate. Phase 2 is the only real engineering
(renderer + migrate mapping) and is the precondition for everything after.
Phase 3 touches the irreplaceable data — it goes only after Phase 2's gate,
and Fletcher only after Spectra. Phases 4–5 are deletions and renames with
the test suite as the net. Total: roughly 6–8 working sessions.

## Out of scope (tracked, not planned here)

- Publication/covers/release module completion (refactor status items).
- Studio feature work beyond module-status awareness.
- The Preludes-and-Symphonies volume reconciliation
  (`transcribe/volumes/01_preludes-and-symphonies-1922/` vs
  `02_dominant_works/`) — a content decision, not a structure one.
