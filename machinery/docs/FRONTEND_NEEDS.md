# Frontend Needs

This file concerns Studio, the machinery frontend in
`machinery/studio/frontend/`. It defines needs and contracts only. Do not treat
this document as scaffolding approval.

## Product Direction

Studio should become the visual and conversational control surface for the
project DAG. A project should open into modules, and each module should behave
like an agent assigned to one stage.

## Required Screens And Modules

### Project Creation

Needs:
- project ID field with slug validation
- title, author/editor, publication type
- intended outputs selector
- initial stage body preview
- workspace registration preview
- create button that can later call a backend project initializer

User inputs:
- project ID
- title
- author/editor
- output targets
- optional persona choice

### Stage Dashboard

Needs:
- DAG visualization
- stage status
- blocked gates
- last verification result
- next required user input
- promotion readiness

### Ingest Module

Needs:
- source list
- PDF inspection panel
- provenance fields
- rights/access status
- proposed filename display
- source manifest preview
- stage chat panel

### Transcribe Module

Needs:
- source page viewer
- transcription editor
- metadata panel
- uncertain-reading queue
- source matter area
- stage chat panel

### Proof Module

Needs:
- audit results
- source/text comparison affordance
- correction queue
- unresolved questions
- proof status gate
- persona-guided editorial review area
- stage chat panel

### Typeset Module

Needs:
- `collection.yaml` editor
- content tree
- build trigger
- build log
- TeX/PDF preview
- layout regime controls
- stage chat panel

### Covers Module

Needs:
- cover asset library
- cover proof preview
- page-count/vendor dependency display
- style records
- approval gate
- stage chat panel

### Front-End Module

Needs:
- public copy editor
- media selector
- static preview
- launch checklist
- stage chat panel

### Final Module

Needs:
- approved artifact list
- checksum/manifest display
- vendor target selector
- release checklist
- final signoff gate
- stage chat panel

### Project Chat Screen

Needs:
- project-wide chat
- stage routing suggestions
- external knowledge citations
- proposed actions and diffs
- user approval before writes

Access model:
- read entire `projects/<project_id>/`
- read stage docs and skills
- consult external knowledge base when configured
- write through stage-bounded actions

## External Knowledge Base

Frontend should display when an answer or suggestion used external knowledge.
Required display fields:

- source title or label
- URL or locator when available
- retrieval timestamp
- affected decision
- stage that consumed the fact

## Design Position

The interface should feel like a literary production room, not a generic SaaS
dashboard. Prefer dense, legible, stage-specific tools. Avoid marketing
composition. Avoid visible teaching copy where the UI can expose state and
actions directly.

## Near-Term Needs

1. Document backend contracts for each module before building new components.
2. Add route/API smoke tests for existing project, cover, build, and preview
   endpoints.
3. Define a project initializer backend contract.
4. Define a stage status API.
5. Define a promotion gate API.
6. Define chat context-loading behavior per module.
7. Define external knowledge citation payloads.

## Verification

```powershell
cd machinery\studio\frontend
npm run typecheck
npm run build
```

Use live backend smoke checks only with local project data present.
