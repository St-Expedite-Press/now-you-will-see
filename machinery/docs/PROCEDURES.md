# Procedures

Use these procedures from the repository root. For the full command reference,
directory taxonomy, and data schemas, read `ONTOLOGY.md`.

---

## Starting a Task

1. Read root `AGENTS.md` — classification tree, routing tables, DAG, update loops.
2. Classify the job type: `pipeline`, `research`, `conversation`, or `tooling`.
   If composite, declare the full path before starting.
3. If pipeline: route to the stage using the pipeline routing table and read the
   stage `AGENTS.md`. If non-pipeline: follow the non-pipeline routing table in
   root `AGENTS.md`. If ambiguous: load `machinery/skills/task-classifier/SKILL.md`.
4. Load only the skill files needed for the specific task.
5. Identify what user input is required before stage completion.
6. Write only to `projects/<project_id>/<stage>/` unless the user approves
   a cross-stage edit.

If the task requires repo-wide context (directory shape, schemas, command
names, invariants), read `ONTOLOGY.md` rather than exploring the filesystem.

---

## Create Local Workspace State

```powershell
Copy-Item workspace.example.yaml workspace.yaml
```

Edit `workspace.yaml` to point at local project typeset roots:

```yaml
projects:
  - id: my-project
    path: projects/my-project/typeset
    description: "Local project"
default_project: my-project
```

---

## Build and Watch

```powershell
# Draft build (fast — skips PDF/X pass, single LaTeX run)
.\.venv\Scripts\texgraph.exe build --project <id> --draft

# Production build (PDF/X-3)
.\.venv\Scripts\texgraph.exe build --project <id>

# Auto-rebuild on file changes
.\.venv\Scripts\texgraph.exe watch --project <id>

# List registered projects
.\.venv\Scripts\texgraph.exe list
```

---

## Carry a Project Through the DAG

At each step, stop and present the required user input before proceeding.

1. **project-create** — collect: project ID, title, author/editor, intended outputs, persona choice if relevant.
2. **ingest** — collect: sources, provenance, rights/access notes, naming approval.
3. **transcribe** — collect: target scope, policy, uncertain readings for resolution.
4. **proof** — collect: correction decisions and unresolved textual questions.
5. **typeset** — collect: trim, format, type regime, inclusion decisions.
6. **covers** — collect: visual direction, assets, page-count-dependent specs.
7. **front-end** — collect: audience, public copy, media, launch mode.
8. **final** — collect: vendor target and final signoff.

See `ONTOLOGY.md § Pipeline Architecture` for the full DAG and stage ownership rules.
See `machinery/docs/DAG_PIPELINE.md` for node contracts and promotion record schema.

---

## Ontology Update Loop

Run after any task that changes directory structure, file formats, CLI commands,
data schemas, or pipeline edges:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

Review and update the flagged `ONTOLOGY.md` sections. Then save a new baseline:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```

Do not save a baseline before updating the flagged sections.

---

## Verify the CLI

```powershell
.\.venv\Scripts\pip.exe install -e .
.\.venv\Scripts\texgraph.exe list
.\.venv\Scripts\python.exe -m pytest machinery\tests -q
```

With a registered project:

```powershell
.\.venv\Scripts\texgraph.exe build --project <id> --draft
```

---

## Run Studio

```powershell
# Install studio dependencies first if not already done
.\.venv\Scripts\pip.exe install -e ".[studio]"

# Launch (opens browser)
.\.venv\Scripts\texgraph.exe studio

# Launch without opening browser
.\.venv\Scripts\texgraph.exe studio --no-open
```

Backend import check:

```powershell
.\.venv\Scripts\python.exe -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('machinery/studio/backend').resolve())); import app.main; print('backend-import-ok')"
```

Frontend checks (requires Node.js 18+):

```powershell
cd machinery\studio\frontend
npm run typecheck
npm run build
```

---

## Verify Font Embedding (Before Vendor Submission)

```powershell
pdffonts projects\<id>\typeset\output\<file>.pdf
```

All fonts must show `emb: yes`. Any un-embedded font will cause a vendor
rejection.

---

## Check What git ls-files Tracks

Before pushing, verify no project data is tracked:

```powershell
git ls-files projects
git ls-files workspace.yaml
```

Both should return empty (except the tracked `spectra_poems` example).
`workspace.yaml` should never be committed.

---

## Stage Procedures

Detailed contracts, skill rosters, and tool references live in each stage's
`AGENTS.md`. Point of entry per task type:

| Task involves | Read |
|---|---|
| Source acquisition, provenance | `ingest/AGENTS.md` |
| Poem or prose transcription | `transcribe/AGENTS.md` |
| Verification, audit, editorial review | `proof/AGENTS.md` |
| Layout, PDF builds | `typeset/AGENTS.md` |
| Cover production | `covers/AGENTS.md` |
| E-reader, web, publication output | `front-end/AGENTS.md` |
| Release packaging | `final/AGENTS.md` |
| CLI, Studio, tests, infrastructure, docs | `machinery/AGENTS.md` |
