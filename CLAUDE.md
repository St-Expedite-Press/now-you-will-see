# Texgraph

**Read `AGENTS.md` before every task.** It is the root dispatcher for all routing
decisions. This file is the entry point; `AGENTS.md` is the authority.

---

## What this project is

Texgraph is a Markdown → LuaLaTeX → PDF/X poetry collection pipeline with an
integrated editorial toolkit. It publishes critical editions of poetry using a
five-stage DAG:

```
ingest → transcribe → proof → typeset → final
```

Stage outputs:
- **ingest**: source files, provenance records
- **transcribe**: Markdown poem source
- **proof**: draft tex+pdf for editorial review (`proof/output/`)
- **typeset**: final production tex+pdf, PDF/X-compliant (`typeset/output/`)
- **final**: packaged release PDF + cover

Each stage is gated by a `PROMOTION.yaml` that requires explicit user approval.
The `texgraph` CLI is the sole command entrypoint.

---

## Before any task

1. **Classify** the job: `pipeline/<stage>` | `research` | `conversation` | `tooling`
   — see `AGENTS.md § Phase 0`.
2. **Route** to the relevant stage `AGENTS.md` or skill.
3. **For pipeline work:** run `texgraph verify <stage>` before writing any files.
   A failed gate is a hard stop.
4. **For transcription work:** check that a transcription plan exists under
   `projects/<id>/transcribe/metadata/transcription_plans/` and that
   `book.md` has an approved checklist before scaffolding or filling poem files.

---

## Mandatory loops

### After any change to infrastructure, CLI, schemas, or pipeline edges

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

If it flags changes, update `ONTOLOGY.md` in the listed sections before closing.
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

### After any stage work

If stage output is complete, check whether `PROMOTION.yaml` needs updating
and whether `texgraph verify <next-stage>` now passes.

---

## Key commands

```powershell
# Gate check (run before starting any stage work)
.\.venv\Scripts\texgraph.exe verify <stage> --project <id>

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

# Proof build (draft tex+pdf → proof/output/)
.\.venv\Scripts\texgraph.exe proof-build --project <id>

# Typeset build (final production → typeset/output/)
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
| `ONTOLOGY.md` | Authoritative repo map: schemas, commands, invariants |
| `<stage>/AGENTS.md` | Stage contract: inputs, outputs, gate, skills, tools |
| `<stage>/RUNBOOK.md` | Operator guide: concrete commands, paths, failure modes |
| `projects/<id>/RUN_REPORT.md` | Session log: what ran, what changed, what remains |
| `workspace.yaml` | Maps project IDs to typeset paths (local, gitignored) |

---

## Critical invariants

- `texgraph` is the sole CLI entrypoint.
- Stage agents write only to `projects/<id>/<stage>/`. No cross-stage writes.
- Persona prose never enters source text, YAML, manifests, or audit output.
- `PROMOTION.yaml` is the machine-readable gate. No silent promotions.
- Stable source naming (`<author>_<year>_<title>_<source>.<ext>`) is the ingest certification.
- `section_id` is the directory name, not `_meta.yaml:id`.

For the full invariant list: `ONTOLOGY.md § Key Invariants`.
