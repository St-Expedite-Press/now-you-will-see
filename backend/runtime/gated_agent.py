"""GatedAgent assembler.

Builds one stage's specialist agent from its framework spec — the system prompt,
persona, the tool allow-list (resolved against the ToolCatalog), the named skills,
the gate, the io contract, and the artifact scope (the stage's project directory).

The assembled agent is *gated*: ``tool_allow`` is the only set of tools the runtime
will let it call, and ``scope`` is the only directory it may write.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from backend.core.env import repo_root
from backend.runtime.tools import ToolCatalog, ToolSpec


@dataclass
class GatedAgent:
    stage: str
    screen: int
    title: str
    module: str
    system_prompt: str
    tools: list[ToolSpec]
    tool_allow: set[str]
    skills: list[str]
    gate: str | None
    io: dict
    scope: Path | None
    upstream: list[str] = field(default_factory=list)

    def allows(self, tool_id: str) -> bool:
        """Is this tool inside the agent's allow-list? (matches stage-suffixed ids)."""
        if tool_id in self.tool_allow:
            return True
        head = " ".join(tool_id.split()[:2])
        return any(head == " ".join(a.split()[:2]) for a in self.tool_allow)


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _skill_descriptions(root: Path) -> dict[str, str]:
    """name -> one-line description, scanned from the loading-contract skill set."""
    out: dict[str, str] = {}
    for p in list((root / "modules").glob("*/skills/*/SKILL.md")) + list(
        (root / "machinery/skills").glob("*/SKILL.md")
    ) + list((root / "framework/agents").glob("*/skills/*/SKILL.md")):
        fm = _read_frontmatter(p)
        name = fm.get("name") or p.parent.name
        out[name] = (fm.get("description") or "").strip()
    return out


def _module_artifact_dir(root: Path, module: str, project_id: str | None) -> Path | None:
    mod_yaml = root / "modules" / module / "module.yaml"
    if not mod_yaml.exists():
        return None
    data = yaml.safe_load(mod_yaml.read_text(encoding="utf-8")) or {}
    art = data.get("artifact_dir")
    if not art:
        return None
    art = art.replace("<project_id>", project_id or "<project_id>")
    return (root / art).resolve()


def assemble_agent(
    stage: str,
    project_id: str | None = None,
    *,
    root: Path | None = None,
    catalog: ToolCatalog | None = None,
) -> GatedAgent:
    """Assemble the gated agent for *stage* from framework/agents/<stage>/agent.yaml."""
    root = (root or repo_root()).resolve()
    catalog = catalog or ToolCatalog()

    spec_path = root / "framework" / "agents" / stage / "agent.yaml"
    if not spec_path.exists():
        raise FileNotFoundError(f"no agent spec for stage {stage!r}: {spec_path}")
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}

    allow = list(spec.get("tools") or [])
    tools = catalog.specs_for(allow)
    skills = list(spec.get("skills") or [])
    descs = _skill_descriptions(root)

    persona_path = root / (spec.get("persona") or "framework/PERSONA.md")
    persona = persona_path.read_text(encoding="utf-8") if persona_path.exists() else ""

    io = spec.get("io") or {}
    module = spec.get("module") or stage
    scope = _module_artifact_dir(root, module, project_id)

    # Compose the system prompt: the spec prompt, the gating contract, the skills it
    # may draw on, the io it must honour, and the persona register.
    parts = [spec.get("system_prompt", "").strip()]
    parts.append(
        "## Your gate\n"
        "You are a gated specialist agent. You may ONLY use the tools provided to you, "
        "and you may write ONLY within your stage's directory"
        + (f" (`{scope}`)." if scope else ".")
    )
    if skills:
        lines = [f"- **{s}** — {descs.get(s, '')}".rstrip(" —") for s in skills]
        parts.append("## Skills you may draw on\n" + "\n".join(lines))
    if io:
        rec = ", ".join(io.get("receives") or []) or "—"
        prod = ", ".join(io.get("produces") or []) or "—"
        parts.append(f"## Hand-off contract\nYou receive: {rec}\nYou must produce: {prod}")
    if persona.strip():
        parts.append("## Editorial register (PERSONA)\n" + persona.strip())

    system_prompt = "\n\n".join(p for p in parts if p.strip())

    return GatedAgent(
        stage=stage,
        screen=int(spec.get("screen", -1)),
        title=spec.get("title", stage),
        module=module,
        system_prompt=system_prompt,
        tools=tools,
        tool_allow={t.id for t in tools},
        skills=skills,
        gate=spec.get("gate"),
        io=io,
        scope=scope,
        upstream=list(spec.get("upstream") or []),
    )
