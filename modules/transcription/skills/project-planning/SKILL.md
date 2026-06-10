---
name: project-planning
description: Consolidate, maintain, and verify project-level publication plans. Use when editing files under projects/<project_id>/transcription/project_plan/, combining planning documents, adding appendices or indexes, aligning plan prose with repo status, source inventory, metadata, tools, and skills.
---

# Project Planning

## Workflow

1. Read `AGENTS.md` and `transcribe/AGENTS.md`.
2. For voice-led or structural plans, read `PERSONA.md` and
   `modules/manuscript/skills/persona-editorial/SKILL.md`.
3. Read the current files under `projects/<project_id>/transcription/project_plan/`,
   plus relevant metadata: source manifest, publication order, and editorial
   policy under `projects/<project_id>/transcription/metadata/`.
4. Check current repo status with deterministic tools before repeating stale
   plan claims:
   ```powershell
   .\.venv\Scripts\texgraph.exe metadata projects/<project_id>/transcription/volumes --check
   .\.venv\Scripts\texgraph.exe plan projects/<project_id>/transcription/project_plan/PROJECT_PLAN.md --check
   ```
5. Separate local repo scope from larger publication horizons.
6. Use appendices for source inventories, rights checklists, production notes,
   tooling notes, and research sources.
7. Include an index for long planning documents.
8. Remove stale AI citation tokens, unresolved scratch notes, and contradicted
   facts when producing a consolidated plan.
9. When a plan implies movement between stages, record the required user gate
   and downstream DAG edge. See `AGENTS.md § DAG` for the pipeline structure.

## Boundaries

Do not put literal transcription work in project plans. Do not let the
configured persona enter YAML, source manifests, audit output, or poem bodies.
