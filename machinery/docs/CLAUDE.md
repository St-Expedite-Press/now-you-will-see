# Texgraph

**Read `AGENTS.md` before every task.** It is the root dispatcher for all routing
decisions. This file is the entry point; `AGENTS.md` is the authority.

---

## What this project is

Texgraph is a Markdown → LuaLaTeX → PDF/X poetry collection pipeline with an
integrated editorial toolkit. It publishes critical editions of poetry using a
canonical module DAG:

```
workspace → sources → transcription → manuscript → interior → [covers, publication] → release
```

Module outputs:
- **workspace**: project registration and local project map
- **sources**: source files and provenance records
- **transcription**: documentary Markdown source
- **manuscript**: corrected manuscript, corrections, and textual review
- **interior**: proof drafts and final production TeX/PDF, PDF/X-compliant
- **covers/publication**: cover and reader-facing deliverables
- **release**: packaged release files

Each module is gated by a `PROMOTION.yaml` that requires explicit user approval.
The `texgraph` CLI is the sole command entrypoint.

---

## Before any task

1. **Classify** the job: `pipeline/<module>` | `research` | `conversation` | `tooling`
   — see `AGENTS.md § Phase 0`.
2. **Route** to the relevant module `AGENTS.md` or skill.
3. **For pipeline work:** run `texgraph verify <module>` before writing any files.
   A failed gate is a hard stop.
4. **For transcription work:** check that a transcription plan exists under
   `projects/<id>/transcription/metadata/transcription_plans/` and that
   `book.md` has an approved checklist before scaffolding or filling poem files.

---

## Mandatory loops

### After any change to infrastructure, CLI, schemas, or pipeline edges

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

If it flags changes, update `machinery/docs/ONTOLOGY.md` in the listed sections before closing.
Then save a new baseline:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```

### After any significant task

Run the skills update loop (`AGENTS.md § Skills Update Loop`):

1. Which skills were loaded? Which should have been?
2. Was there friction, a missing instruction, or a tool gap?
3. Fix obvious low-risk issues in the relevant `SKILL.md` now.
4. Record broader fixes as follow-ups.

### After any module work

If module output is complete, check whether `PROMOTION.yaml` needs updating
and whether `texgraph verify <next-module>` now passes.

---

## Key commands

```powershell
# Gate check (run before starting any module work)
.\.venv\Scripts\texgraph.exe verify <module> --project <id>

# Approve a module gate (writes status: approved to PROMOTION.yaml)
.\.venv\Scripts\texgraph.exe promote <module> --project <id>

# Source acquisition
.\.venv\Scripts\texgraph.exe archive files <identifier>
.\.venv\Scripts\texgraph.exe archive download <id> <file> <dest>
.\.venv\Scripts\texgraph.exe pdf info <pdf>
.\.venv\Scripts\texgraph.exe pdf render <pdf> --first N --last N --prefix P
.\.venv\Scripts\texgraph.exe pdf text <pdf> --first N --last N --output <file>

# Ingest
.\.venv\Scripts\texgraph.exe ingest rename <file> --author A --year Y --title T --source S --project <id>

# Transcription validation
.\.venv\Scripts\texgraph.exe audit <book_dir>
.\.venv\Scripts\texgraph.exe metadata <volumes_dir> --write --check
.\.venv\Scripts\texgraph.exe page-map --offset N --printed "<ranges>"
.\.venv\Scripts\texgraph.exe scan <volumes_dir> --output <path>

# Module registry and migration
.\.venv\Scripts\texgraph.exe modules list
.\.venv\Scripts\texgraph.exe modules verify interior --project <id>
.\.venv\Scripts\texgraph.exe migrate modules --project <id> --dry-run

# Proof build (draft tex+pdf → interior/output/proof/)
.\.venv\Scripts\texgraph.exe proof-build --project <id>

# Interior build (final production → interior/output/)
.\.venv\Scripts\texgraph.exe build --project <id>
.\.venv\Scripts\texgraph.exe build --project <id> --draft
.\.venv\Scripts\texgraph.exe watch --project <id>

# Ontology
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```

---

## Key files

| File | Purpose |
|---|---|
| `AGENTS.md` | Root dispatcher — read first |
| `machinery/docs/ONTOLOGY.md` | Authoritative repo map: schemas, commands, invariants |
| `modules/<module>/AGENTS.md` | Module contract: inputs, outputs, gate, skills, tools |
| `modules/<module>/RUNBOOK.md` | Operator guide when present: concrete commands, paths, failure modes |
| `projects/<id>/RUN_REPORT.md` | Index of dated session reports in `projects/<id>/reports/` |
| `projects/<id>/manuscript/EDITORIAL_PROCEDURE.md` | Reading-edition format: three-section poem files, note classes |
| `workspace.yaml` | Maps project IDs to project/interior roots (local, gitignored) |

---

## Critical invariants

- `texgraph` is the sole CLI entrypoint.
- Module agents write only to the active module artifact directory. No cross-module writes.
- Persona prose never enters source text, YAML, manifests, or audit output.
- `PROMOTION.yaml` is the machine-readable gate. No silent promotions.
- Stable source naming (`<author>_<year>_<title>_<source>.<ext>`) is the sources certification.
- `section_id` is the directory name, not `_meta.yaml:id`.

For the full invariant list: `machinery/docs/ONTOLOGY.md § Key Invariants`.
