# Tool Proposals

These tools are proposed by the current framework intent. They are not all
implemented.

## Project And DAG Tools

- `texgraph init-project <id>`: create the full module directory body and seed
  `interior/collection.yaml`.
- `texgraph dag status --project <id>`: show module completion, blocked gates,
  and downstream readiness.
- `texgraph promote --project <id> --module <module>`: create or approve a
  promotion record after user approval.
- `texgraph gate --project <id> --module <module>`: list required user inputs for
  module completion.
- `texgraph doctor`: check venv, LuaLaTeX, Node, workspace, project shape, and
  module directories.

## Sources Tools

- `texgraph source add`: register a source file with provenance metadata.
- `texgraph source manifest --check`: validate source manifest entries against
  files on disk.
- `texgraph rights check`: record rights/access status without making legal
  claims.

## Transcription Tools

- `texgraph transcribe scaffold`: create transcription targets from a source
  manifest or contents page.
- `texgraph source compare-pages`: compare declared scan/printed page ranges
  against rendered images.
- `texgraph uncertainty list`: collect unresolved readings across a project.

## Manuscript Tools

- `texgraph proof report`: generate a proof report from audit findings,
  unresolved readings, and metadata status.
- `texgraph proof apply-corrections`: apply reviewed correction records.

## Interior And Release Tools

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
- module write guards
- promotion-record writer
- user-input checklist generator
