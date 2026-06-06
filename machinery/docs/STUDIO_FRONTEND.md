# Studio Frontend

This is the canonical development document for Texgraph Studio frontend work.
Do not split Studio frontend routes, module plans, design rules, or test
commands into other docs.

## Scope

Studio is the local React/FastAPI control surface under `machinery/studio/`.
It is machinery, not a pipeline stage.

Publication-facing web, EPUB, reader, and launch assets belong to the project
stage `projects/<project_id>/front-end/` and the root `front-end/` framework.
Do not mix that stage with Studio frontend development.

## Source Locations

```text
machinery/studio/backend/       FastAPI backend
machinery/studio/frontend/      React + Vite + TypeScript frontend
machinery/studio/backend/static Built frontend assets served by FastAPI
```

Main frontend entry points:

```text
src/App.tsx
src/pages/StudioHome.tsx
src/pages/ProjectSelect.tsx
src/pages/ProjectConfig.tsx
src/pages/IngestProjectPicker.tsx
src/pages/IngestDocuments.tsx
src/pages/ProjectEditor.tsx
src/pages/AuditDashboard.tsx
```

## Current Routes

```text
/                         Studio entry
/ingest                   Ingest project picker
/projects                 Continue Project
/projects/new             Create Project
/projects/<id>/ingest     Ingest Documents wireframe
/projects/<id>            Project editor
```

Project editor view modes include cards, graph, build, covers, agent, and audit
where available.

## Current Implementation

Implemented:

- Studio entry screen with Ingest Documents, Create Project, Continue Project,
  and Return Home.
- Continue Project list using `GET /api/projects`.
- Project Creation module using existing `POST /api/projects`.
- Ingest project picker using `GET /api/projects`.
- Project-scoped Ingest Documents wireframe with mocked gate state and stable
  filename preview.
- Project editor cards view.
- Build panel with streaming build logs.
- Covers scaffold.
- Graph scaffold.
- Agent panel that sends raw chat messages.
- Product Readiness Audit dashboard using `POST /api/audit/run`.

Not implemented:

- Live `PROMOTION.yaml` gate state across Studio.
- `texgraph promote` UI.
- Classification-aware agent routing.
- Programmatic action-chip execution.
- Ingest backend routes for project-scoped source lists, stable-name preview,
  and source registration.
- EPUB/web publication output. That belongs to the `front-end/` pipeline stage.

## Design Position

The Studio UI should feel like an independent literary production workbench:
simple, aesthetic, post-corporate, and honest about unfinished behavior.

Use:

- thin dividers over heavy cards
- restrained controls
- direct labels
- stage-specific tools
- plain status language
- disabled states for mocked or future behavior

Avoid:

- marketing pages
- generic SaaS dashboard composition
- hidden planned-work claims
- implying stages promote themselves
- visible teaching copy where state and actions can carry the interface

## Backend Contracts Used Today

```text
GET  /api/projects
POST /api/projects
GET  /api/projects/{id}
POST /api/projects/{id}/build
GET  /api/projects/{id}/preview
POST /api/agent
POST /api/audit/run
GET  /health
```

Project Creation submits only the backend fields currently accepted:

```text
id
path
description
meta.title
meta.author
meta.subtitle
meta.year
meta.publisher
meta.isbn
```

Wireframe-only project creation fields must stay local UI state until backend
storage exists:

```text
publicationType
outputTargets
initialStage
```

## Future Backend Contracts

These are design targets, not current API guarantees:

```text
GET  /api/projects/{project_id}/ingest
POST /api/projects/{project_id}/ingest/preview-name
POST /api/projects/{project_id}/ingest/sources
GET  /api/projects/{project_id}/gates
POST /api/projects/{project_id}/promote/{stage}
```

The promote route should not exist until the CLI promotion behavior is real and
requires explicit user approval.

## Development Setup

From the repository root:

```powershell
.\.venv\Scripts\pip.exe install -e ".[studio]"
```

Install frontend dependencies:

```powershell
cd machinery\studio\frontend
npm install
```

Build frontend assets for FastAPI:

```powershell
npm run build
cd ..\..\..
```

Launch Studio:

```powershell
.\.venv\Scripts\texgraph.exe studio
```

Launch without opening a browser:

```powershell
.\.venv\Scripts\texgraph.exe studio --no-open
```

Default URL:

```text
http://127.0.0.1:8765
```

## Test Procedure

Run these from the repository root unless noted.

### Backend Import

```powershell
.\.venv\Scripts\python.exe -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('machinery/studio/backend').resolve())); import app.main; print('backend-import-ok')"
```

### Frontend Typecheck And Build

```powershell
cd machinery\studio\frontend
npm run typecheck
npm run build
cd ..\..\..
```

The build writes compiled assets to `machinery/studio/backend/static/`.

### Studio Route Smoke Checks

Start Studio first:

```powershell
.\.venv\Scripts\texgraph.exe studio --no-open
```

In another PowerShell session:

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/).StatusCode
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/ingest).StatusCode
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/projects).StatusCode
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/projects/new).StatusCode
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/projects/spectra_poems/ingest).StatusCode
```

Each should return `200` when `spectra_poems` is registered in `workspace.yaml`.

### API Smoke Checks

With Studio running:

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health).StatusCode
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/api/projects).StatusCode
Invoke-WebRequest -Uri http://127.0.0.1:8765/api/audit/run -Method POST -UseBasicParsing
```

### Python Regression Tests

```powershell
.\.venv\Scripts\python.exe -m pytest machinery\tests -q
```

### Example Project Build

```powershell
.\.venv\Scripts\texgraph.exe list
.\.venv\Scripts\texgraph.exe build --project spectra_poems --draft
```

## Expected Warnings

Vite may warn that a built JavaScript chunk is larger than 500 kB. That warning
does not fail the build. Treat it as a future code-splitting task, not a broken
frontend.

## Next Frontend Work

1. Add route-level smoke tests for Studio entry, project creation, continue
   project, ingest picker, and project-scoped ingest.
2. Add live pipeline gate API and UI.
3. Add DAG graph state using real `PROMOTION.yaml` verification output.
4. Add ingest backend contracts.
5. Add classification-aware agent startup.
6. Add promote UI after `texgraph promote` exists.
7. Persist audit runs after the read-only audit contract stabilizes.
