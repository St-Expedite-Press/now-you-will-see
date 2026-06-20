"""HandoffController — move from one stage's agent to the next.

A handoff happens only when the current stage's gate (``PROMOTION.yaml``) is
approved. The next stage's agent is then assembled and seeded with the prior
stage's ``io.produces`` — the "jumping-off point" for the next screen.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from backend.core.env import repo_root
from backend.runtime.gated_agent import GatedAgent, assemble_agent
from backend.runtime.tools import ToolCatalog


class GateNotPassed(RuntimeError):
    pass


@dataclass
class Handoff:
    next_agent: GatedAgent
    seed: str  # an initial context message for the next agent


class HandoffController:
    def __init__(self, root: Path | None = None, catalog: ToolCatalog | None = None) -> None:
        self.root = (root or repo_root()).resolve()
        self.catalog = catalog or ToolCatalog()
        self._pipeline = yaml.safe_load(
            (self.root / "framework" / "pipeline.yaml").read_text(encoding="utf-8")
        )

    def order(self) -> list[str]:
        """Linear station order, flattened from pipeline screens."""
        out: list[str] = []
        for screen in self._pipeline.get("screens", []):
            for stage in screen.get("stages", []):
                if stage not in out:
                    out.append(stage)
        return out

    def next_stage(self, stage: str) -> str | None:
        order = self.order()
        if stage not in order:
            return None
        i = order.index(stage)
        return order[i + 1] if i + 1 < len(order) else None

    def gate_passed(self, agent: GatedAgent, project_id: str | None) -> bool:
        if not agent.gate:
            return True  # no gate (e.g. editorial layer) — passes implicitly
        gate_path = self.root / agent.gate.replace("<project_id>", project_id or "")
        if not gate_path.exists():
            return False
        data = yaml.safe_load(gate_path.read_text(encoding="utf-8")) or {}
        return str(data.get("status", "")).lower() == "approved"

    def advance(
        self,
        current: GatedAgent,
        project_id: str | None = None,
        *,
        prior_outputs: dict | None = None,
    ) -> Handoff | None:
        """Assemble + seed the next stage's agent, if the current gate is passed."""
        if not self.gate_passed(current, project_id):
            raise GateNotPassed(
                f"{current.stage} gate not approved; cannot hand off to the next stage."
            )
        nxt = self.next_stage(current.stage)
        if nxt is None:
            return None
        next_agent = assemble_agent(nxt, project_id, root=self.root, catalog=self.catalog)
        produced = current.io.get("produces") or []
        outputs = prior_outputs or {k: "(produced)" for k in produced}
        lines = [f"- {k}: {v}" for k, v in outputs.items()]
        seed = (
            f"Handoff from the {current.stage} stage. It produced:\n"
            + "\n".join(lines)
            + f"\n\nYou are the {next_agent.title} agent. Begin from these inputs."
        )
        return Handoff(next_agent=next_agent, seed=seed)
