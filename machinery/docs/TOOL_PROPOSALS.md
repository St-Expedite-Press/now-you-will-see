# Tool Proposals

These tools are proposed by the current framework intent. They are not all
implemented.

## Project And DAG Tools

- `texgraph init-project <id>`: create the full stage directory body and seed
  `typeset/collection.yaml`.
- `texgraph dag status --project <id>`: show stage completion, blocked gates,
  and downstream readiness.
- `texgraph promote --project <id> --from <stage> --to <stage>`: create a
  promotion record after user approval.
- `texgraph gate --project <id> --stage <stage>`: list required user inputs for
  stage completion.
- `texgraph doctor`: check venv, LuaLaTeX, Node, workspace, project shape, and
  stage directories.

## Ingest Tools

- `texgraph source add`: register a source file with provenance metadata.
- `texgraph source manifest --check`: validate source manifest entries against
  files on disk.
- `texgraph rights check`: record rights/access status without making legal
  claims.

## Transcribe Tools

- `texgraph transcribe scaffold`: create transcription targets from a source
  manifest or contents page.
- `texgraph source compare-pages`: compare declared scan/printed page ranges
  against rendered images.
- `texgraph uncertainty list`: collect unresolved readings across a project.

## Proof Tools

- `texgraph proof report`: generate a proof report from audit findings,
  unresolved readings, and metadata status.
- `texgraph proof apply-corrections`: apply reviewed correction records.

## Typeset And Final Tools

- `texgraph build-manifest --project <id>`: record build inputs, output files,
  versions, and engine details.
- `texgraph pdf inspect --project <id>`: inspect page count, embedded fonts,
  PDF standard, and trim assumptions.
- `texgraph final package --project <id>`: assemble approved artifacts and
  checksums.

## Studio/Agent Tools

- module-specific chat context loaders
- external knowledge retrieval adapter
- project-wide read-only indexer
- stage write guards
- promotion-record writer
- user-input checklist generator
