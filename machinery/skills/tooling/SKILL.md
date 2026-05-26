---
name: tooling
description: Use and maintain deterministic repo-local Python tools. Use when creating, running, or updating stage tools, enforcing the repo .venv, wiring stage skills to helpers for PDF inspection, page mapping, audits, source matter scanning, book.json metadata, and research efficiency.
---

# Tooling

## Venv Rule

Run Python tools only through the repo-local venv:

```powershell
.\.venv\Scripts\python.exe <stage>\tools\<script>.py ...
```

If `.venv` is missing, create it with `python -m venv .venv` before running
repo tools. Keep tools standard-library unless a dependency is clearly needed;
record dependencies in `requirements.txt`.

## Tool Rules

1. Keep scripts deterministic and command-line driven.
2. Put reusable Python helpers in the owning stage's `tools/` directory.
3. Make scripts reject execution outside the repo venv.
4. Use scripts to accelerate inspection, mapping, auditing, and cleanup.
5. Do not use tools to replace page-image review for transcription.
6. Document new tools in the relevant stage `AGENTS.md` or `tools/README.md`
   and reference them from relevant stage `skills/*/SKILL.md`.
7. For DAG tools, document the stage inputs, outputs, required user gate, and
   downstream edge.
8. Use `book_metadata.py` after structural changes to generate or validate
   per-book `book.json` files.
9. Use `source_matter_scan.py` after source acquisition or replacement to
   refresh source front/back matter signals, then visually review image-only or
   ambiguous sources before transcription.
10. Proposed tool contracts belong in `machinery/docs/TOOL_PROPOSALS.md` until
    the user approves implementation.

## Common Commands

These commands are compatibility entrypoints into the same system:

```powershell
fletcher metadata projects\fletcher-complete-original-collections\transcribe\volumes --write --check
fletcher scan projects\fletcher-complete-original-collections\transcribe\volumes --output projects\fletcher-complete-original-collections\transcribe\metadata\source_matter_inventory.md
fletcher plan projects\fletcher-complete-original-collections\transcribe\project_plan\PROJECT_PLAN.md --check
```

Use CLI `--check` modes in verification-only contexts. Use `--write` only when
the task allows metadata changes.

