# Data Dictionary

This file records stable public contracts for the framework. The code is the
final source of truth when implementation details diverge.

## Workspace

Tracked template:

```text
workspace.example.yaml
```

Local workspace file:

```text
workspace.yaml
```

Shape:

```yaml
projects:
  - id: example-project
    project_root: projects/example-project
    path: projects/example-project/interior
    modules:
      sources: projects/example-project/sources
      transcription: projects/example-project/transcription
      manuscript: projects/example-project/manuscript
      interior: projects/example-project/interior
      covers: projects/example-project/covers
      publication: projects/example-project/publication
      release: projects/example-project/release
    description: "Local project workspace"
default_project: example-project
```

## Project

Project body:

```text
projects/<project_id>/
  covers/
  interior/
  manuscript/
  publication/
  release/
  sources/
  transcription/

  # compatibility-only paths accepted during one release cycle:
  ingest/
  transcribe/
  proof/
  typeset/
  front-end/
  final/
```

Buildable roots are `projects/<project_id>/interior`. Unmigrated projects may
still build from `projects/<project_id>/typeset`.

## Module Node

Conceptual shape for a module in the DAG:

```yaml
module: transcription
project_id: example-project
inputs_required:
  - approved source files
  - transcription policy
outputs_expected:
  - transcribed markdown
  - metadata updates
user_gate:
  - uncertain readings resolved or recorded
downstream:
  - manuscript
```

## Promotion Record

Planned shape:

```yaml
from_module: transcription
to_module: interior
project_id: example-project
approved_by: user
approved_at: 2026-05-26T00:00:00Z
inputs:
  - path: projects/example-project/transcription
outputs:
  - path: projects/example-project/interior
notes: ""
```

Promotion records are documented but not yet automated.

## Interior Project

Expected local shape:

```text
projects/<project_id>/interior/
  collection.yaml
  content/
  output/
```

`output/` is generated.

## Section

Identity key: filesystem directory name.

Example:

```text
content/03_vibrations-dented-spheres/
```

Do not use `_meta.yaml:id` as the API or lookup identifier.

## Poem

Identity key: markdown filename stem.

Example:

```text
harmonikum.md
```

The poem body remains documentary. Editorial or institutional prose belongs in
the appropriate project/module files, not inside source transcription by
accident.

## Version Sidecar

Version sidecars use this naming pattern:

```text
.slug.versions.yaml
```

Canonical version selection must match build behavior.

## Module Registry

Canonical module order:

```text
workspace -> sources -> transcription -> manuscript -> interior -> [covers, publication] -> release
```

Legacy aliases resolve as follows:

```yaml
ingest: sources
transcribe: transcription
proof: manuscript
typeset: interior
front-end: publication
final: release
```

`proof` is legacy support for proofing skills and historical records. It is not
a canonical pipeline stage.

## Studio Module Agent

Planned conceptual shape:

```yaml
module: interior
project_id: example-project
read_scope: projects/example-project
write_scope: projects/example-project/interior
external_knowledge: optional
requires_user_gate: true
```

Module agents may read the full project directory. Writes should stay in the
active module path unless the user approves a cross-module edit or promotion.

## Studio Product Readiness Audit

Implemented API contract:

```text
POST /api/audit/run
```

The audit is read-only and returns an `AuditRun` envelope:

```yaml
id: audit-<opaque>
created_at: 2026-06-06T00:00:00+00:00
repo_root: C:/path/to/Texgraph
persona: burned_out_bay_area_engineer
frontend_framework: react
mode: read_only
target: texgraph_current_system
status: complete
subagents: []
report: null
```

Subagents return `AuditSubagentResult` objects with `findings`, `evidence`, and
`open_questions`. Evidence kinds are `file`, `command`, `test`, `doc`, `api`,
and `ui`. Findings use `critical`, `high`, `medium`, or `low` severity.

This audit is a product-readiness inspection of Texgraph itself. It is not a
pipeline proof artifact and must not write to source text, YAML manifests, or
project module directories.

## Module Skills

Skills are module-owned:

- `modules/sources/skills/`
- `modules/transcription/skills/`
- `modules/manuscript/skills/`
- `modules/interior/skills/`
- `machinery/skills/`

Add new skills to the module that owns the job. Legacy root skill directories
remain only for compatibility.
