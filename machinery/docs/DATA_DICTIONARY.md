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
    path: projects/example-project/typeset
    description: "Local project workspace"
default_project: example-project
```

## Project

Project body:

```text
projects/<project_id>/
  ingest/
  transcribe/
  proof/
  typeset/
  final/
  covers/
  front-end/
```

Buildable roots are `projects/<project_id>/typeset`.

## Stage Node

Conceptual shape for a stage in the DAG:

```yaml
stage: transcribe
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
  - proof
```

## Promotion Record

Planned shape:

```yaml
from_stage: proof
to_stage: typeset
project_id: example-project
approved_by: user
approved_at: 2026-05-26T00:00:00Z
inputs:
  - path: projects/example-project/transcribe
outputs:
  - path: projects/example-project/typeset
notes: ""
```

Promotion records are documented but not yet automated.

## Typeset Project

Expected local shape:

```text
projects/<project_id>/typeset/
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
the appropriate project/stage files, not inside source transcription by
accident.

## Version Sidecar

Version sidecars use this naming pattern:

```text
.slug.versions.yaml
```

Canonical version selection must match build behavior.

## Studio Module Agent

Planned conceptual shape:

```yaml
module: proof
project_id: example-project
read_scope: projects/example-project
write_scope: projects/example-project/proof
external_knowledge: optional
requires_user_gate: true
```

Module agents may read the full project directory. Writes should stay in the
active stage unless the user approves a cross-stage edit or promotion.

## Stage Skills

Skills are stage-owned:

- `ingest/skills/`
- `transcribe/skills/`
- `proof/skills/`
- `typeset/skills/`
- `machinery/skills/`

Add new skills to the stage that owns the job.
