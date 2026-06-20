---
name: tooling
description: "Use and maintain deterministic repo-local Python tools. Use when creating, running, or updating stage tools, enforcing the repo .venv, wiring stage skills to helpers for PDF inspection, page mapping, audits, source matter scanning, book.json metadata, and research efficiency."
module: machinery
tools:
  - tools/ontology_check.py
  - tools/skill_index.py
---
# Tooling

## Venv Rule

Run Python tools only through the repo-local venv:

```powershell
.\.venv\Scripts\python.exe <stage>\tools\<script>.py ...
.\.venv\Scripts\texgraph.exe <command> ...
```

If `.venv` is missing, create it with `python -m venv .venv` then install:

```powershell
.\.venv\Scripts\pip.exe install -e .
.\.venv\Scripts\pip.exe install -e ".[studio]"
```

Keep tools standard-library unless a dependency is clearly needed; record
new dependencies in `requirements.txt` and `pyproject.toml`.

## Tool Rules

1. Keep scripts deterministic and command-line driven.
2. Put reusable Python helpers in the owning stage's `tools/` directory.
3. Put cross-stage infrastructure helpers in `tools/`.
4. Use scripts to accelerate inspection, mapping, auditing, and cleanup.
5. Do not use tools to replace page-image review for transcription decisions.
6. Document new tools in the relevant stage `AGENTS.md` tools section.
7. For DAG tools, document: stage inputs, outputs, required user gate, downstream edge.
8. Use `texgraph metadata` after structural changes to generate or validate
   per-book `book.json` files.
9. Use `texgraph scan` after source acquisition or replacement to refresh
   source front/back matter signals.
10. Proposed tool contracts belong in `README.md` until
    the user approves implementation.

## Common Commands

```powershell
# Build and watch
.\.venv\Scripts\texgraph.exe build --project <id> --draft
.\.venv\Scripts\texgraph.exe watch --project <id>

# Metadata and audit
.\.venv\Scripts\texgraph.exe metadata projects/<project_id>/transcribe/volumes --write --check
.\.venv\Scripts\texgraph.exe scan projects/<project_id>/transcribe/volumes --output projects/<project_id>/transcribe/metadata/source_matter_inventory.md
.\.venv\Scripts\texgraph.exe plan projects/<project_id>/transcribe/project_plan/PROJECT_PLAN.md --check
.\.venv\Scripts\texgraph.exe audit projects/<project_id>/transcribe/<volume>/books/<book>

# PDF inspection
.\.venv\Scripts\texgraph.exe pdf info <pdf>
.\.venv\Scripts\texgraph.exe pdf render <pdf> --first <n> --last <n> --prefix <prefix>
.\.venv\Scripts\texgraph.exe pdf text <pdf> --first <n> --last <n>

# Ontology checker
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```

Use CLI `--check` modes in verification-only contexts. Use `--write` only when
the task allows metadata changes.
