---
name: skill-improvement-loop
description: "Review and improve repo-local skills after each task. Use at the end of every task in this repo to assess whether AGENTS.md or files under stage skills/ directories should be clarified, generalized, split, or updated based on what was learned."
module: framework
tools:
  - tools/skill_index.py
---
# Skill Improvement Loop

## End-Of-Task Review

At the end of every task:

1. Identify which repo-local skills were used or should have been used.
2. Note any friction, missing instruction, repeated command, unclear boundary,
   source-specific exception, tool gap, MCP gap, or verification gap.
   In this repo, explicitly check whether the task changed expectations around
   DAG edges, user gates, promotion records, stage inputs/outputs, module-agent
   behavior, external knowledge use, `book.json`, source front/back matter,
   source inventory, or volume-level apparatus.
3. If the improvement is obvious and low risk, update `AGENTS.md`, `framework/PERSONA.md`,
   or the relevant stage `skills/*/SKILL.md` before final response.
4. If the improvement is speculative or broad, mention it as a proposed follow-up
   in the final response instead of editing.
5. Keep skill, tool, and persona updates generalized. Do not bake one-off page
   readings or task results into reusable skills.

## Final Response

Include a short skill review in the final response:

- skills used
- improvements made, if any
- remaining skill improvement ideas, if useful

