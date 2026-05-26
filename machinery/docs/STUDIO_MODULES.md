# Studio Module Plan

Studio should become the control surface for the DAG pipeline. No frontend
scaffolding is added by this document. It defines the modules the future
frontend needs.

## Product Shape

Studio should present a project as a set of stage modules plus one project-wide
chat screen. Each module behaves like a bounded agent:

- it can read the entire project directory
- it can consult an external knowledge base when configured
- it writes primarily to its owning stage
- it asks for user input at promotion gates
- it explains the evidence behind suggested transitions

## Required Modules

### Project Creation Module

Purpose:
- create a project ID and directory body
- collect title, author/editor, publication type, intended outputs
- initialize `workspace.yaml`
- initialize `typeset/collection.yaml`

Required user inputs:
- project ID
- title
- author/editor
- output targets
- initial stage selection

### Ingest Module

Purpose:
- register sources
- inspect PDFs
- capture provenance
- propose stable filenames
- flag rights or access uncertainty

Required user inputs:
- source selection
- rights/provenance acceptance
- naming approval

### Transcribe Module

Purpose:
- show source pages beside transcription targets
- run page-map and metadata helpers
- stage source matter and poem text
- surface uncertain readings

Required user inputs:
- target book/section
- transcription policy
- uncertain reading decisions

### Proof Module

Purpose:
- run audits
- compare text against source images
- collect corrections
- manage verified/blocked status
- invoke persona only for editorial framing

Required user inputs:
- correction approval
- unresolved textual decisions
- proof pass acceptance

### Typeset Module

Purpose:
- edit/inspect `collection.yaml`
- build drafts
- preview TeX/PDF
- manage layout regime decisions
- record build notes

Required user inputs:
- trim
- type regime
- inclusion/exclusion decisions
- draft and final proof approval

### Covers Module

Purpose:
- inspect cover assets
- connect cover dimensions to page count and vendor specs
- manage cover proofs
- prepare vendor-ready files

Required user inputs:
- visual direction
- selected assets
- vendor target
- proof approval

### Front-End Module

Purpose:
- prepare public/project-facing pages
- manage copy and media
- preview static outputs
- coordinate release call-to-action

Required user inputs:
- audience
- approved copy
- media selection
- launch mode

### Final Module

Purpose:
- collect approved interior, cover, proof, and front-end artifacts
- create release manifest
- verify checksums and required files
- produce handoff package

Required user inputs:
- vendor/release target
- final signoff

### Project Chat Screen

Purpose:
- project-wide question answering and planning
- cross-stage task decomposition
- external knowledge retrieval
- routing into modules

Access:
- read access to entire `projects/<project_id>/`
- read access to stage docs and skills
- external knowledge base access when configured

Write behavior:
- no direct cross-stage writes without user approval
- should create proposed actions, diffs, or stage jobs

## External Knowledge Base

The external knowledge base may include:

- rights references
- bibliographic records
- vendor specifications
- style manuals
- project memory
- prior release notes
- source catalogs

Any external fact that affects source status, rights, textual decisions, or
vendor output must be cited in project notes or promotion records.
