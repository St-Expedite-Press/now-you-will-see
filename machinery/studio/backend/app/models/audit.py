"""Pydantic v2 models for the product readiness audit orchestrator."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


AuditVerdict = Literal[
    "not_ready",
    "promising_not_ready",
    "narrowly_usable",
    "ready_for_limited_users",
    "product_ready",
]
AuditRunStatus = Literal["pending", "running", "complete", "failed"]
SubagentStatus = Literal["pass", "warn", "fail", "blocked"]
FindingSeverity = Literal["critical", "high", "medium", "low"]
EvidenceKind = Literal["file", "command", "test", "doc", "api", "ui"]


class EvidenceRef(BaseModel):
    id: str
    kind: EvidenceKind
    path: str | None = None
    command: str | None = None
    observed: str


class Finding(BaseModel):
    severity: FindingSeverity
    claim: str
    evidence_refs: list[str]
    product_risk: str
    recommended_next_step: str


class AuditSubagentResult(BaseModel):
    id: str
    name: str
    category: str
    status: SubagentStatus
    score: int = Field(..., ge=0)
    max_score: int = Field(default=10, ge=1)
    findings: list[Finding] = []
    evidence: list[EvidenceRef] = []
    open_questions: list[str] = []


class ReadinessReport(BaseModel):
    one_sentence_product: str
    specific_user: str
    works_today_without_founder: list[str]
    breaks_first: list[str]
    next_risk_reducing_milestone: str
    verdict: AuditVerdict
    category_scores: dict[str, int]
    executive_summary: str
    highest_risk_assumption: str
    priority_findings: list[Finding]


class AuditRun(BaseModel):
    id: str
    created_at: str
    repo_root: str
    persona: Literal["burned_out_bay_area_engineer"] = "burned_out_bay_area_engineer"
    frontend_framework: Literal["react"] = "react"
    mode: Literal["read_only"] = "read_only"
    target: Literal["texgraph_current_system"] = "texgraph_current_system"
    status: AuditRunStatus
    subagents: list[AuditSubagentResult]
    report: ReadinessReport | None = None
