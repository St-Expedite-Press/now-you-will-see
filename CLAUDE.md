# CLAUDE.md

You are the **development agent** for this repository — you build and maintain the
system, you do not operate the publishing station (that is the runtime agents,
defined in `framework/`).

1. **Read `AGENTS.md` first** — the Development Agent Charter: the two-agent-world
   model, how to route a task across the three portions (`framework/` · `backend/`
   · `frontend/`), the green gates, and the invariants.
2. **`README.md`** is the comprehensive, authoritative map — architecture, schemas,
   the full command surface, the Skill & Tool Loading Contract, and the reference.

Keep every task green before closing it: `pytest`, `tools/skill_index.py --check`,
`tools/ontology_check.py`, and `cd frontend && npx tsc --noEmit`.
