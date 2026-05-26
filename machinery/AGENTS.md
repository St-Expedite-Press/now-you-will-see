# Machinery

Owns executable code, shared infrastructure, tests, and repository maintenance.

## Use For

- Python packages under `src/`.
- Studio backend and frontend under `studio/`.
- Shared tests under `tests/`.
- Technical docs under `docs/`.
- Cross-stage repository structure and tool policy.

## DAG Contract

Inputs:
- requested framework behavior
- compatibility constraints
- affected stage contracts
- verification expectations

Outputs:
- CLI, Studio, test, doc, or skill changes
- proposed tool contracts
- updated verification commands

User gate:
- user approves scope for compatibility breaks, new tools, new modules, and
  stage contract changes.

## Local Skills

- `skills/repo-maintenance/SKILL.md`
- `skills/tooling/SKILL.md`
- `skills/skill-improvement-loop/SKILL.md`

## Tools

Stage-specific tools live in each stage's `tools/` directory. Put only
cross-stage infrastructure helpers in `tools/`.

Keep command names stable: `texgraph` and `fletcher`. Treat them as
compatibility entrypoints into one project DAG and one stage vocabulary.

When changing Python package structure, update `pyproject.toml`. When changing
Studio paths, update `machinery/src/texgraph/cli.py`, backend service path
injection, frontend docs, and verification commands together.
