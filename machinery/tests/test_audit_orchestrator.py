from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "studio" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.models.audit import AuditRun, AuditSubagentResult, EvidenceRef, Finding, ReadinessReport
from app.services import audit_service


def test_audit_schema_validation() -> None:
    finding = Finding(
        severity="high",
        claim="Promotion is not executable.",
        evidence_refs=["gate-code"],
        product_risk="Users must edit gate files manually.",
        recommended_next_step="Implement promote.",
    )
    subagent = AuditSubagentResult(
        id="pipeline-gates",
        name="Pipeline/Gate Auditor",
        category="Pipeline and gates",
        status="warn",
        score=6,
        findings=[finding],
        evidence=[
            EvidenceRef(
                id="gate-code",
                kind="file",
                path="machinery/src/texgraph/promotions.py",
                observed="verify exists",
            )
        ],
    )
    report = ReadinessReport(
        one_sentence_product="A local publishing pipeline.",
        specific_user="Small press editors.",
        works_today_without_founder=["Build a draft PDF."],
        breaks_first=["Promotion gates."],
        next_risk_reducing_milestone="Implement promotion.",
        verdict="promising_not_ready",
        category_scores={"Pipeline and gates": 6},
        executive_summary="Real work, not ready.",
        highest_risk_assumption="Users can infer manual gates.",
        priority_findings=[finding],
    )
    run = AuditRun(
        id="audit-test",
        created_at="2026-06-06T00:00:00+00:00",
        repo_root=str(ROOT.parent),
        status="complete",
        subagents=[subagent],
        report=report,
    )

    assert run.mode == "read_only"
    assert run.frontend_framework == "react"
    assert run.subagents[0].max_score == 10


def test_run_audit_with_mocked_commands() -> None:
    calls: list[list[str]] = []

    def runner(args: list[str], cwd: Path) -> tuple[int, str]:
        calls.append(args)
        return 0, "ok"

    run = audit_service.run_audit(command_runner=runner)

    assert run.status == "complete"
    assert run.report is not None
    assert run.report.verdict in {
        "not_ready",
        "promising_not_ready",
        "narrowly_usable",
        "ready_for_limited_users",
        "product_ready",
    }
    assert len(run.subagents) == 9
    assert any(agent.id == "ai-reliability" for agent in run.subagents)
    assert any("texgraph.exe" in " ".join(args) for args in calls)
    assert any(args[:3] == ["npm", "run", "typecheck"] for args in calls)
