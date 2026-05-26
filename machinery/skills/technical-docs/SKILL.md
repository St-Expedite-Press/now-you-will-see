---
name: technical-docs
description: Maintain and update Texgraph repo documentation: ONTOLOGY.md, stage AGENTS.md files, SKILL.md files, and README. Use when changing directory structure, file formats, CLI commands, data schemas, or pipeline edges requires documentation to be kept in sync.
---

# Technical Documentation

## Use When

Load this skill when the task is documentation maintenance:

- Updating `ONTOLOGY.md` after structural or schema changes
- Rewriting a stage `AGENTS.md` to reflect new contracts or skills
- Writing or updating a `SKILL.md` for a new or changed workflow
- Updating `README.md` after significant capability changes
- Running the ontology checker and acting on its output
- Keeping docs in sync after CLI command changes, dependency changes,
  or pipeline edge changes

Do not use for: poem transcription, typesetting decisions, proof work, or
ingest operations. For infrastructure code changes, use `machinery/AGENTS.md`
and `machinery/skills/tooling`.

## Required Reads

Before any documentation change:

- `ONTOLOGY.md` — current authoritative repo reference
- `AGENTS.md` — root dispatcher contract
- The stage `AGENTS.md` relevant to the change (if updating a stage doc)
- The relevant `SKILL.md` files (if updating skills)

## Ontology Update Protocol

After any task that changes directory structure, file formats, CLI commands,
data schemas, or pipeline edges, run the ontology checker:

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py
```

The checker compares the current git state against a stored baseline and
reports which `ONTOLOGY.md` sections need review.

### Acting on checker output

The checker groups changes into categories and names the `ONTOLOGY.md` section
to review:

| Category | Section to update |
|---|---|
| `schema` | Data Schemas section |
| `commands` | Command Surface section |
| `structure` | Directory Taxonomy and Pipeline Architecture |
| `skills` | Content-type routing table |
| `infrastructure` | Command Surface and Key Invariants |
| `dependencies` | Dependency Map section |

Update every flagged section before saving a new baseline.

### Save baseline after update

```powershell
.\.venv\Scripts\python.exe machinery\tools\ontology_check.py --save-baseline
```

Do not save a new baseline until `ONTOLOGY.md` has been updated.

## ONTOLOGY.md Update Rules

- **Directory Taxonomy**: add/remove/rename any directory or file type
- **Data Schemas**: add/remove/rename any YAML field; new file type conventions
- **Command Surface**: any `texgraph` or `fletcher` command change (new, renamed, removed)
- **Pipeline Architecture**: new stage, changed DAG edge, new gate requirement
- **Key Invariants**: new must-be-true fact, or removal of a constraint
- **Dependency Map**: new Python package, removed package, new external binary

Keep each section in ONTOLOGY.md tight — one authoritative source, no repetition.

## Stage AGENTS.md Conventions

A stage `AGENTS.md` should contain only:

1. **Contract header**: what this stage receives, what it produces, where it writes
2. **Gate**: what user input is required before stage completion or promotion
3. **Skills roster**: which SKILL.md files are available and when to load each
4. **Tools**: which `texgraph` commands this stage uses
5. **Invariants**: stage-specific rules (2–4 bullet points max)

A stage `AGENTS.md` should NOT contain:
- Repository layout (in ONTOLOGY.md)
- Full command reference (in ONTOLOGY.md)
- Content duplicated from root `AGENTS.md`
- Workflow steps that belong in a SKILL.md

Target: 40–60 lines per stage `AGENTS.md`.

## SKILL.md Conventions

Every `SKILL.md` must have:

- **YAML frontmatter**: `name` (kebab-case slug), `description` (one line, specific)
- **Use When**: precise conditions for loading this skill; explicit anti-cases
- **Required Reads**: files to read before acting
- **Workflow or checklist**: actionable steps, not narrative
- **Guardrails**: what this skill must never do

A SKILL.md should not:
- Hardcode project-specific paths — use `projects/<project_id>/`
- Duplicate content from ONTOLOGY.md — reference it
- Describe the tool's general operation — describe *this workflow*

## Skills Update Loop

At the end of every significant task:

1. Which skills were loaded for this task?
2. Was there friction, missing instruction, unclear boundary, or tool gap?
3. If the fix is obvious and low-risk: update the relevant SKILL.md now.
4. If speculative or broad: note it as a proposed follow-up.
5. Never bake one-off task results into reusable skills.

See `machinery/skills/skill-improvement-loop/SKILL.md` for the full loop.

## Guardrails

- Do not update `ONTOLOGY.md` speculatively — only when a tracked area actually changed.
- Do not save a new baseline before updating the flagged sections.
- Do not duplicate content across ONTOLOGY.md, AGENTS.md, and SKILL.md — each has one home.
- Documentation changes that affect stage contracts require explicit user review
  before committing.
