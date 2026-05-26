---
name: project-planning
description: Consolidate, maintain, and verify project-level Fletcher publication plans. Use when editing files under projects/fletcher-complete-original-collections/transcribe/project_plan/, combining planning dumps, adding appendices or indexes, aligning plan prose with four-volume repo status, source inventory, book.json metadata, tools, and skills.
---

# Project Planning

## Workflow

1. Read `AGENTS.md`.
2. For voice-led or structural plans, read `PERSONA.md` and
   `proof/skills/persona-editorial/SKILL.md`.
3. Read the current files under `projects/fletcher-complete-original-collections/transcribe/project_plan/`, plus relevant metadata:
   `projects/fletcher-complete-original-collections/transcribe/metadata/source_manifest.md`, `projects/fletcher-complete-original-collections/transcribe/metadata/publication_order.md`, and
   `projects/fletcher-complete-original-collections/transcribe/metadata/editorial_policy.md`.
4. Check current repo status with deterministic tools before repeating stale
   plan claims.
   - `fletcher metadata volumes --check`
   - `fletcher plan project_plan\PROJECT_PLAN.md --check`
5. Separate local repo scope from larger publication horizons.
6. Use appendices for source inventories, rights checklists, production notes,
   tooling notes, and research sources.
7. Include an index for long planning documents.
8. Remove stale AI citation tokens, unresolved scratch notes, and contradicted
   facts when producing a consolidated plan.
9. When a plan implies movement between stages, record the required user gate
   and downstream DAG edge.

## Tooling

Use the repo venv:

```powershell
fletcher plan project_plan\PROJECT_PLAN.md --check
```

Use `project_index.py` to inspect headings and catch missing appendices, missing
indexes, duplicate heading anchors, or stale citation tokens.

## Boundaries

Do not put literal transcription work in project plans. Do not let the
configured persona enter YAML, source manifests, audit output, or poem bodies.

