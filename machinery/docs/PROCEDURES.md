# Procedures

Use these procedures from the repository root.

## Start A Task

1. Read root `AGENTS.md`.
2. Decompose the request into stage jobs.
3. Identify the DAG node for each job.
4. Read each relevant stage `AGENTS.md`.
5. Read only the local skills needed for that stage.
6. List required user inputs before claiming a stage is complete.
7. Keep writes inside the active stage unless the user approves a cross-stage
   edit or promotion.

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

## Carry A Project Through The DAG

1. `project-create`: collect project ID, title, author/editor, outputs, persona
   choice if relevant.
2. `ingest`: collect sources, provenance, rights/access notes, naming approval.
3. `transcribe`: collect target scope, policy, source uncertainties.
4. `proof`: collect correction decisions and unresolved textual questions.
5. `typeset`: collect trim, format, type regime, inclusion decisions.
6. `covers`: collect visual direction, assets, page-count-dependent specs.
7. `front-end`: collect audience, public copy, media, launch mode.
8. `final`: collect vendor target and final signoff.

Every transition requires user approval. When unsure, stop at a proposed
promotion with evidence.

## Verify The CLI

```powershell
.\.venv\Scripts\pip.exe install -e .
.\.venv\Scripts\texgraph.exe list
.\.venv\Scripts\python.exe -m pytest machinery\tests -q
```

With local project data present:

```powershell
.\.venv\Scripts\texgraph.exe build --project <project_id> --draft
```

## Run Studio

```powershell
.\.venv\Scripts\texgraph.exe studio --no-open
```

Backend import check:

```powershell
.\.venv\Scripts\python.exe -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('machinery/studio/backend').resolve())); import app.main; print('backend-import-ok')"
```

Frontend checks:

```powershell
cd machinery\studio\frontend
npm run typecheck
npm run build
```

## Stage Procedures

- Source intake: read `ingest/AGENTS.md`.
- Transcription and planning: read `transcribe/AGENTS.md`.
- Audits and editorial review: read `proof/AGENTS.md`.
- Layout and builds: read `typeset/AGENTS.md`.
- Cover production: read `covers/AGENTS.md`.
- Publication-facing front ends: read `front-end/AGENTS.md`.
- Release packaging: read `final/AGENTS.md`.
- Code, Studio, tests, repo structure: read `machinery/AGENTS.md`.

## Publishing Boundary Check

Before publishing framework changes:

```powershell
git ls-files projects
git ls-files workspace.yaml
```

Both commands should return no tracked files for the public framework repo.
