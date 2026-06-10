# Modular Refactor Audit Status

Date: 2026-06-09

## Verdict

The modular refactor is implemented and usable as a compatibility-first
transition. The canonical registry, CLI module commands, migration planner,
promotion verification, and Studio module APIs are present. Existing projects
have not been migrated yet; they continue to work through aliases.

## Confirmed Implemented

- Root `modules/` tree exists for `workspace`, `sources`, `transcription`,
  `manuscript`, `interior`, `covers`, `publication`, `release`, `studio`, and
  `platform`.
- Each module has `AGENTS.md`, `module.yaml`, and local `src/`, `tests/`,
  `skills/`, `schemas/`, and `tools/` folders.
- Shared module registry lives at `machinery/src/texgraph/modules.py`.
- Compatibility aliases resolve legacy public names for one release cycle:
  `ingest`, `transcribe`, `proof`, `typeset`, `front-end`, and `final`.
- `texgraph modules list`, `texgraph modules verify <module>`, and
  `texgraph migrate modules --project <id> --dry-run|--apply` are available.
- `texgraph verify interior` and `texgraph verify typeset` use the same
  upstream transcription gate during compatibility.
- `texgraph proof-build` targets proof draft output under the resolved
  interior root. Migrated projects use `interior/output/proof`; unmigrated
  projects continue to use `typeset/output/proof`.
- Studio has module list/detail/verify backend APIs and frontend module status
  awareness.
- DAG semantics are corrected: `covers` depends on approved `interior`, and
  `release` consumes approved `interior` plus optional approved covers and
  publication artifacts.

## Verification Snapshot

Passing checks from the refactor audit:

- `.\.venv\Scripts\python.exe -m pytest machinery\tests -q`
- `.\.venv\Scripts\python.exe -m compileall machinery\studio\backend\app machinery\src\texgraph`
- `npm run typecheck` from `machinery/studio/frontend`
- `.\.venv\Scripts\texgraph.exe modules list`
- `.\.venv\Scripts\texgraph.exe modules verify sources`
- `.\.venv\Scripts\texgraph.exe modules verify interior`
- `.\.venv\Scripts\texgraph.exe modules verify typeset`
- `.\.venv\Scripts\texgraph.exe modules verify proof`
- `.\.venv\Scripts\texgraph.exe migrate modules --project spectra_poems --dry-run`
- `.\.venv\Scripts\texgraph.exe migrate modules --project fletcher-complete-original-collections --dry-run`

## Current Drift and Risk

- Legacy root directories still exist and still contain redirect or compatibility
  docs. This is intentional for one release cycle, but searches will still find
  old names.
- Tracked projects are not yet migrated. Fletcher and Spectra remain in legacy
  project artifact directories until `texgraph migrate modules --apply` is run.
- `workspace.yaml` compatibility remains path-centered. Canonical
  `project_root` and explicit module artifact roots are documented, but older
  `path` values are still accepted.
- `texgraph promote <module>` is still missing. Users must still approve gates
  by editing PROMOTION.yaml manually.
- Publication, covers, and release are structurally present but not yet
  production-complete modules.
- Static Studio build assets may contain older labels from the compiled frontend
  bundle; source files are the canonical edit targets.

## Documentation Audit Results

Updated during this audit:

- `AGENTS.md`
- `machinery/docs/README.md`
- `machinery/docs/PROJECT_OVERVIEW.md`
- `machinery/docs/ONTOLOGY.md`
- `machinery/docs/HANDOFF.md`
- `machinery/docs/CLAUDE.md`
- `machinery/docs/PERSONA.md`
- `machinery/docs/DATA_DICTIONARY.md`
- `machinery/docs/DAG_PIPELINE.md`
- `machinery/docs/PROCEDURES.md`
- `machinery/docs/TOOL_PROPOSALS.md`

Root `README.md`, `ONTOLOGY.md`, `HANDOFF.md`, `CLAUDE.md`, and `PERSONA.md`
are now compatibility stubs. Canonical long-form documentation lives under
`machinery/docs/`. Remaining compatibility references are acceptable only when
they are explicitly described as aliases or legacy paths. New operator
instructions should point to `machinery/docs/*`, `modules/<module>/AGENTS.md`,
and semantic project directories.

## Next Hardening Sequence

1. Add `texgraph promote <module>` so approval writes are no longer manual.
2. Apply module migration to one low-risk project and validate build/proof-build.
3. Apply module migration to the Fletcher project after reviewing dry-run output.
4. Add `modules/interior/RUNBOOK.md` for proof draft and production PDF builds.
5. Replace old root stage docs with short `LEGACY.md` redirects once no current
   docs route new work through them.
6. Add broader CLI integration tests for `ingest rename`, `verify`, `modules
   verify`, and migration conflict behavior.
