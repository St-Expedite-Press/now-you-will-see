# Procedures

Use these procedures from the repository root. For the full command reference,
directory taxonomy, and data schemas, read `machinery/docs/ONTOLOGY.md`.

---

## Starting a Task

1. Read root `AGENTS.md` — classification tree, routing tables, DAG, update loops.
2. Classify the job type: `pipeline`, `research`, `conversation`, or `tooling`.
   If composite, declare the full path before starting.
3. If pipeline: route to the module using the pipeline routing table and read the
   module's `modules/<module>/AGENTS.md`. If non-pipeline: follow the non-pipeline routing table in
   root `AGENTS.md`. If ambiguous: load `machinery/skills/task-classifier/SKILL.md`.
4. Load only the skill files needed for the specific task.
5. Identify what user input is required before module completion.
6. Write only to the module-owned project path unless the user approves
   a cross-module edit.

If the task requires repo-wide context (directory shape, schemas, command
names, invariants), read `machinery/docs/ONTOLOGY.md` rather than exploring the filesystem.

---

## Create Local Workspace State

```powershell
Copy-Item workspace.example.yaml workspace.yaml
```

Edit `workspace.yaml` to point at local project roots and interior roots:

```yaml
projects:
  - id: my-project
    project_root: projects/my-project
    path: projects/my-project/interior
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

# Build proof artifact tree and proof PDF (trade style sheet)
.\.venv\Scripts\texgraph.exe proof-build --project <id>

# Build a variant style sheet (hardcover / softcover) through the SAME proof
# pipeline — writes to interior/output/proof-<name>/ so it never clobbers the trade proof
.\.venv\Scripts\texgraph.exe proof-build --config projects/<id>/interior/collection_hardcover.yaml

# List registered projects
.\.venv\Scripts\texgraph.exe list
```

---

## Visual Proof Review

Never sign off a typeset proof by reading the generated `.tex`. Render the
structurally important leaves and look at them:

```powershell
# Renders book title pages, part dividers, and any sparse/short-poem pages to
# interior/output/proof/preview/*.png  (requires pdftoppm + pdftext from poppler)
.\.venv\Scripts\texgraph.exe proof-preview --project <id>

# Add explicit pages or a sampling stride
.\.venv\Scripts\texgraph.exe proof-preview --project <id> --pages 40,120-122 --sample 50
```

The tool auto-detects structural pages by content (a near-empty leaf is a title
page, a divider, a short centered poem, or — a defect — an orphaned line or a
stray-folio blank). Inspect each rendered PNG. This loop is what catches
orphaned closing couplets, split stanzas, and blank leaves carrying a folio —
none of which appear in a grep of the source.

---

## Batch / Agent Edits to Source

When a script or sub-agent rewrites many manuscript files (e.g. an editorial
note pass), make each write idempotent and self-checkpointing: write results
back to the source file as each unit completes, so a crash or interrupted run is
resumable by re-running over only the not-yet-updated files. Never hold a whole
batch in memory to write at the end — a process exit loses all of it. Because the
Fletcher manuscript is now version-controlled (see git tracking below), commit
before a large batch so a bad rewrite is recoverable with `git restore`.

---

## Carry a Project Through the DAG

At each step, stop and present the required user input before proceeding.

1. **workspace** — collect: project ID, title, author/editor, intended outputs, persona choice if relevant.
2. **sources** — collect: sources, provenance, rights/access notes, naming approval.
3. **transcription** — collect: target scope, policy, uncertain readings for resolution.
4. **manuscript** — collect: correction decisions and unresolved textual questions.
5. **interior** — collect: trim, format, type regime, inclusion decisions.
6. **covers** — collect: visual direction, assets, page-count-dependent specs.
7. **publication** — collect: audience, public copy, media, launch mode.
8. **release** — collect: vendor target and final signoff.

See `machinery/docs/ONTOLOGY.md § Pipeline Architecture` for the full DAG and module ownership rules.
See `machinery/docs/DAG_PIPELINE.md` for node contracts and promotion record schema.

---

## Ontology Update Loop

Run after any task that changes directory structure, file formats, CLI commands,
data schemas, or pipeline edges:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

Review and update the flagged `machinery/docs/ONTOLOGY.md` sections. Then save a new baseline:

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

## Verify Font Embedding (Before Vendor Submission)

```powershell
pdffonts projects\<id>\interior\output\<file>.pdf
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

`workspace.yaml` should return empty. `projects/` may show tracked exception
workspaces such as `spectra_poems` and `fletcher-complete-original-collections`;
raw ingest files and generated PDFs should not be tracked.

---

## Stage Procedures

Detailed contracts, skill rosters, and tool references live in each module's
`AGENTS.md`. Point of entry per task type:

| Task involves | Read |
|---|---|
| Source acquisition, provenance | `modules/sources/AGENTS.md` |
| Poem or prose transcription | `modules/transcription/AGENTS.md` |
| Verification, audit, editorial review | `modules/manuscript/AGENTS.md` |
| Layout, PDF builds | `modules/interior/AGENTS.md` |
| Cover production | `modules/covers/AGENTS.md` |
| E-reader, web, publication output | `modules/publication/AGENTS.md` |
| Release packaging | `modules/release/AGENTS.md` |
| CLI, Studio, tests, infrastructure, docs | `machinery/AGENTS.md` |
