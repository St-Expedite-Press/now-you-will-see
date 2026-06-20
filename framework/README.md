# framework/ — Agentic Framework / Knowledge Base

The **runtime-agnostic** definition of the publishing station's specialist agents.
This is the portable artifact that loads onto the production runtime (**Hermes**) and
that the dev backend runtime (`backend/runtime/`) instantiates. It is *data and
knowledge*, not executable code.

```
framework/
  pipeline.yaml              the DAG: stages → station screens, gates, hand-off io contracts
  agents/<stage>/agent.yaml  per-stage agent spec: system prompt, persona, tool allow-list,
                             gate, io contract, skills
  PERSONA.md                 editorial house-voice register the agents may adopt
  loading_contract           the Skill & Tool Index (in README.md) generated/validated by
                             tools/skill_index.py — the static context + permission manifest
```

## How a gated agent is assembled

For a station screen, the runtime builds one **gated specialist agent** from:

1. **`agents/<stage>/agent.yaml`** — the system prompt, persona, the **tool
   allow-list** (a subset of the stage module's command surface), the **gate**
   (`PROMOTION.yaml`), and the **io contract** (what it receives from the prior
   stage and must produce for the next).
2. **The stage's skills** (named in `agent.yaml: skills`) — loaded by relevance from
   the Skill & Tool Index, never the whole skill surface.
3. **Artifact scope** — the stage's project directory (`modules/<stage>` declares
   `artifact_dir`); the agent may write only there.

On gate approval, the `HandoffController` activates the next stage's agent seeded
with the prior stage's `produces` outputs ("prior inputs as the jumping-off point").

## Two-agent worlds

- **Runtime agents** (defined here, run on Hermes): operate the station for end users.
- **Development agent** (Claude Code, charter in root `AGENTS.md`/`CLAUDE.md`): builds
  and maintains the whole system — including this framework.

## Validation

`tools/skill_index.py --check` validates every `agent.yaml` (required fields; tools
resolve to real CLI commands; referenced skills exist; `stage` matches the directory)
and keeps the Skill & Tool Index in sync. Run `--write` after editing a spec or skill.

> Note: stage **skills** currently live with their backend module
> (`modules/<stage>/skills/`) and `machinery/skills/` and are referenced by name;
> physically co-locating them under `agents/<stage>/skills/` for full portability is a
> pending hygiene step.
