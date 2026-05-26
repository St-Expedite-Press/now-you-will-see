# Application Plan

Studio is the local control surface for carrying a project through the stage
DAG. Studio is machinery. Publication-facing sites and static deliverables
belong to the `front-end/` stage.

## Intent

Studio should make the pipeline visible. A user should be able to create a
project, enter a stage module, see what inputs are required, work with a
stage-specific agent, consult external knowledge when configured, and promote
approved outputs to the next stage.

The current repo documents this intended product shape. It does not add new
frontend scaffolding in this pass.

## Current Position

As of May 26, 2026:

- Studio backend lives in `machinery/studio/backend/`.
- Studio frontend lives in `machinery/studio/frontend/`.
- The system launches Studio through `texgraph studio`.
- Project data is local under `projects/`.
- `workspace.yaml` is local; `workspace.example.yaml` is the public template.
- The framework is organized around stage agents and stage-local skills/tools.
- Root `AGENTS.md` defines the project DAG and promotion gates.
- `texgraph` and `fletcher` are compatibility command entrypoints into one
  project DAG.

## Studio Modules

Required future modules:

1. Project Creation Module
2. Ingest Module
3. Transcribe Module
4. Proof Module
5. Typeset Module
6. Covers Module
7. Front-End Module
8. Final Module
9. Project Chat Screen

Each module acts as an agent surface:

- read access to the entire project directory
- optional access to an external knowledge base
- stage-bounded writes by default
- user-input checklist for completion
- promotion suggestions with evidence

See `STUDIO_MODULES.md` for the module contracts.

## User-Gated Promotion

The frontend should never imply that stages silently promote themselves. Each
stage needs a visible gate:

- required inputs
- completed outputs
- unresolved questions
- verification results
- user approval action

Promotion records are planned in `DAG_PIPELINE.md`.

## Working Baseline

Expected checks:

```powershell
.\.venv\Scripts\texgraph.exe list
.\.venv\Scripts\python.exe -m pytest machinery\tests -q

cd machinery\studio\frontend
npm run typecheck
npm run build
```

With a local project registered:

```powershell
.\.venv\Scripts\texgraph.exe build --project <project_id> --draft
```

## Roadmap

1. Add project creation workflow around the full stage directory body.
2. Add module navigation for each DAG stage.
3. Add user-input checklists per module.
4. Add stage status and promotion readiness indicators.
5. Add project-wide chat with route-to-stage actions.
6. Add external knowledge retrieval with citation/provenance capture.
7. Add promotion-record storage and display.
8. Add smoke tests for CLI, backend import, route health, and frontend build.

Where this file conflicts with code, the code wins.
