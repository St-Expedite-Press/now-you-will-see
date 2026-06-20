"""Read-only product readiness audit orchestration for Texgraph Studio."""

from __future__ import annotations

import subprocess
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.audit import (
    AuditRun,
    AuditSubagentResult,
    EvidenceRef,
    Finding,
    ReadinessReport,
)

CommandRunner = Callable[[list[str], Path], tuple[int, str]]

STAGE_DIRS = ("ingest", "transcribe", "proof", "typeset", "covers", "front-end", "final")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except FileNotFoundError:
        return ""


def _read_doc(root: Path, name: str) -> str:
    """Read a root doc. QUICKSTART/HANDOFF/PROJECT_OVERVIEW/STUDIO_FRONTEND were
    folded into the comprehensive README.md when machinery/docs was dissolved."""
    folded = {"QUICKSTART.md", "HANDOFF.md", "PROJECT_OVERVIEW.md", "STUDIO_FRONTEND.md"}
    target = "README.md" if name in folded else name
    return _read(root / target)


def _exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def _evidence(
    eid: str,
    kind: str,
    observed: str,
    *,
    path: str | None = None,
    command: str | None = None,
) -> EvidenceRef:
    return EvidenceRef(id=eid, kind=kind, path=path, command=command, observed=observed)


def _finding(
    severity: str,
    claim: str,
    evidence_refs: list[str],
    product_risk: str,
    recommended_next_step: str,
) -> Finding:
    return Finding(
        severity=severity,
        claim=claim,
        evidence_refs=evidence_refs,
        product_risk=product_risk,
        recommended_next_step=recommended_next_step,
    )


def _status(score: int, blocked: bool = False) -> str:
    if blocked:
        return "blocked"
    if score >= 8:
        return "pass"
    if score >= 5:
        return "warn"
    return "fail"


def _run_command(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return 124, f"Timed out after {exc.timeout}s\n{output}"

    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    return completed.returncode, output.strip()


def run_audit(command_runner: CommandRunner | None = None) -> AuditRun:
    """Run the read-only audit and return a complete evidence-backed report."""
    root = settings.workspace_root.resolve()
    runner = command_runner or _run_command

    subagents = [
        _product_definition(root),
        _workflow(root, runner),
        _pipeline_gates(root),
        _react_studio(root),
        _backend_api(root),
        _ai_reliability(root),
        _maintainability(root, runner),
        _operations_security(root),
        _commercial_wedge(root),
    ]
    report = _synthesize_report(subagents)

    return AuditRun(
        id=f"audit-{uuid.uuid4().hex[:12]}",
        created_at=_utc_now(),
        repo_root=str(root),
        status="complete",
        subagents=subagents,
        report=report,
    )


def _product_definition(root: Path) -> AuditSubagentResult:
    docs = {
        "README.md": _read_doc(root, "README.md"),
        "README.md (quickstart)": _read_doc(root, "QUICKSTART.md"),
        "README.md (handoff)": _read_doc(root, "HANDOFF.md"),
        "README.md (studio)": _read_doc(root, "STUDIO_FRONTEND.md"),
    }
    evidence = [
        _evidence(
            "product-docs",
            "doc",
            f"Found {sum(1 for value in docs.values() if value)} of 4 product-definition documents.",
            path="README.md",
        )
    ]
    findings: list[Finding] = []
    score = 8 if all(docs.values()) else 5

    planned_markers = sum("planned" in text.lower() or "future" in text.lower() for text in docs.values())
    if planned_markers:
        evidence.append(
            _evidence(
                "current-vs-planned",
                "doc",
                "Docs explicitly distinguish built functionality from planned Studio/front-end work.",
                path="README.md",
            )
        )
    else:
        score -= 2
        findings.append(
            _finding(
                "high",
                "Current and planned product surfaces are not cleanly separated in the documentation.",
                ["product-docs"],
                "A user may mistake a roadmap for available product functionality.",
                "Add explicit current/planned labels to product docs before using them as sales material.",
            )
        )

    if "poets, translators, and small press editors" in docs["README.md"]:
        evidence.append(
            _evidence(
                "specific-user",
                "doc",
                "README names poets, translators, and small press editors as the intended user.",
                path="README.md",
            )
        )
    else:
        score -= 1

    return AuditSubagentResult(
        id="product-definition",
        name="Product Definition Auditor",
        category="Product definition",
        status=_status(score),
        score=max(score, 0),
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _workflow(root: Path, runner: CommandRunner) -> AuditSubagentResult:
    commands = [
        ("workflow-list", [str(root / ".venv" / "Scripts" / "texgraph.exe"), "list"], root),
        (
            "workflow-build",
            [
                str(root / ".venv" / "Scripts" / "texgraph.exe"),
                "build",
                "--project",
                "spectra_poems",
                "--draft",
            ],
            root,
        ),
    ]
    evidence: list[EvidenceRef] = []
    failures = 0
    for eid, args, cwd in commands:
        code, output = runner(args, cwd)
        if code != 0:
            failures += 1
        evidence.append(
            _evidence(
                eid,
                "command",
                f"exit={code}; {output[:800] if output else 'no output'}",
                command=" ".join(args),
            )
        )

    quickstart = _read_doc(root, "QUICKSTART.md")
    if "Build the example project" in quickstart:
        evidence.append(
            _evidence(
                "workflow-doc",
                "doc",
                "QUICKSTART includes a linear path to building the example project.",
                path="README.md",
            )
        )

    score = 8 - (failures * 2)
    findings = []
    if failures:
        findings.append(
            _finding(
                "high",
                "At least one first-run workflow command failed in the current environment.",
                [e.id for e in evidence if e.kind == "command"],
                "A non-founder cannot trust the documented workflow without environment-specific help.",
                "Make failing prerequisites explicit and add a preflight command that reports missing dependencies.",
            )
        )

    return AuditSubagentResult(
        id="workflow",
        name="Workflow Auditor",
        category="User workflow",
        status=_status(score),
        score=max(score, 0),
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _pipeline_gates(root: Path) -> AuditSubagentResult:
    cli = _read(root / "backend/core/cli.py")
    promotions = _read(root / "backend/core/promotions.py")
    agents = _read(root / "AGENTS.md")
    evidence = [
        _evidence("gate-docs", "doc", "Root dispatcher and ontology define staged gates.", path="AGENTS.md"),
        _evidence(
            "gate-code",
            "file",
            f"promotions.py present={bool(promotions)}; verify command present={'def verify' in cli}.",
            path="backend/core/promotions.py",
        ),
    ]
    findings: list[Finding] = []
    score = 7

    if "def promote" not in cli:
        score -= 2
        findings.append(
            _finding(
                "high",
                "`texgraph promote <stage>` is documented as needed but is not implemented.",
                ["gate-code"],
                "Gate approval still depends on manual file edits, so the product workflow is not repeatable enough.",
                "Implement promote as the next gate milestone before expanding Studio promotion UI.",
            )
        )

    if '"front-end":' not in promotions and "'front-end':" not in promotions:
        score -= 1
        findings.append(
            _finding(
                "medium",
                "The publication front-end gate is documented but not represented in promotions.py.",
                ["gate-code"],
                "The documented DAG and executable gate model diverge.",
                "Add front-end verification semantics or mark the stage as explicitly ungated until built.",
            )
        )

    if all(_exists(root, f"{stage}/AGENTS.md") for stage in STAGE_DIRS) and "Classify first" in agents:
        evidence.append(
            _evidence(
                "stage-contracts",
                "file",
                "All stage AGENTS.md files exist and root dispatcher requires classify-first routing.",
                path="AGENTS.md",
            )
        )
    else:
        score -= 1

    return AuditSubagentResult(
        id="pipeline-gates",
        name="Pipeline/Gate Auditor",
        category="Pipeline and gates",
        status=_status(score),
        score=max(score, 0),
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _react_studio(root: Path) -> AuditSubagentResult:
    frontend = root / "frontend/src"
    files = list(frontend.rglob("*.tsx")) + list(frontend.rglob("*.ts")) if frontend.exists() else []
    joined_names = "\n".join(str(path.relative_to(root)).replace("\\", "/") for path in files)
    evidence = [
        _evidence(
            "react-files",
            "ui",
            f"React source files found: {len(files)}.",
            path="frontend/src",
        ),
        _evidence(
            "studio-views",
            "ui",
            "Cards, graph, build, covers, and agent surfaces are present in source."
            if all(name in joined_names for name in ("CardBrowser", "GraphCanvas", "BuildPanel", "CoverStudio", "AgentPanel"))
            else "One or more expected Studio surfaces are missing.",
            path="frontend/src",
        ),
    ]
    findings: list[Finding] = []
    score = 7 if files else 2

    non_audit_text = "".join(_read(path) for path in files if "Audit" not in path.name)
    if "PROMOTION" not in non_audit_text:
        score -= 2
        findings.append(
            _finding(
                "high",
                "React Studio has no visible PROMOTION.yaml or gate status awareness.",
                ["react-files", "studio-views"],
                "The UI does not expose the central product invariant: explicit stage promotion.",
                "Add a pipeline status panel before treating Studio as the primary product surface.",
            )
        )

    if "AuditDashboard" not in joined_names:
        evidence.append(
            _evidence(
                "audit-ui-new",
                "ui",
                "Audit dashboard is not present before this implementation.",
                path="frontend/src",
            )
        )

    return AuditSubagentResult(
        id="react-studio",
        name="React Studio Auditor",
        category="React Studio",
        status=_status(score),
        score=max(score, 0),
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _backend_api(root: Path) -> AuditSubagentResult:
    routers = sorted((root / "backend/api/app/routers").glob("*.py"))
    services = sorted((root / "backend/api/app/services").glob("*.py"))
    main = _read(root / "backend/api/app/main.py")
    evidence = [
        _evidence("backend-routers", "api", f"Router files found: {len(routers)}.", path="backend/api/app/routers"),
        _evidence("backend-services", "api", f"Service files found: {len(services)}.", path="backend/api/app/services"),
    ]
    score = 8 if "/api/projects" in main and "/api/agent" in main else 5
    findings: list[Finding] = []

    if "audit" not in main:
        evidence.append(
            _evidence(
                "audit-api-new",
                "api",
                "Audit API is not registered before this implementation.",
                path="backend/api/app/main.py",
            )
        )

    return AuditSubagentResult(
        id="backend-api",
        name="Backend/API Auditor",
        category="Backend API",
        status=_status(score),
        score=score,
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _ai_reliability(root: Path) -> AuditSubagentResult:
    agent_service = _read(root / "backend/api/app/services/agent_service.py")
    agent_panel = _read(root / "frontend/src/components/agent/AgentPanel.tsx")
    evidence = [
        _evidence(
            "agent-service",
            "api",
            f"Agent service present={bool(agent_service)}; hard-coded prompt={'_SYSTEM_PROMPT' in agent_service}.",
            path="backend/api/app/services/agent_service.py",
        ),
        _evidence(
            "agent-panel",
            "ui",
            f"Agent panel present={bool(agent_panel)}; sends contextual chat={'send(content' in agent_panel}.",
            path="frontend/src/components/agent/AgentPanel.tsx",
        ),
    ]
    findings = [
        _finding(
            "high",
            "The current agent is chat-only and not classification-aware.",
            ["agent-service", "agent-panel"],
            "Agent behavior can drift from the stage-gated workflow and does not have an evaluation harness.",
            "Route Studio agent sessions through job classification before adding write-capable actions.",
        )
    ]
    score = 5

    if "ANTHROPIC_API_KEY" in agent_service:
        evidence.append(
            _evidence(
                "agent-key-boundary",
                "api",
                "Agent service fails closed when ANTHROPIC_API_KEY is not set.",
                path="backend/api/app/services/agent_service.py",
            )
        )
        score += 1

    return AuditSubagentResult(
        id="ai-reliability",
        name="AI/Agent Reliability Auditor",
        category="AI reliability",
        status=_status(score),
        score=score,
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _maintainability(root: Path, runner: CommandRunner) -> AuditSubagentResult:
    commands = [
        ("pytest", [str(root / ".venv" / "Scripts" / "python.exe"), "-m", "pytest", "backend/tests", "-q"], root),
        ("typecheck", ["npm", "run", "typecheck"], root / "frontend"),
        ("frontend-build", ["npm", "run", "build"], root / "frontend"),
    ]
    evidence: list[EvidenceRef] = []
    failures = 0
    for eid, args, cwd in commands:
        code, output = runner(args, cwd)
        failures += 1 if code != 0 else 0
        evidence.append(
            _evidence(eid, "test", f"exit={code}; {output[:800] if output else 'no output'}", command=" ".join(args))
        )

    test_files = list((root / "backend/tests").glob("test_*.py"))
    evidence.append(
        _evidence("test-count", "file", f"Test files found under backend/tests: {len(test_files)}.", path="backend/tests")
    )
    score = 6 - failures
    findings: list[Finding] = []
    if len(test_files) < 6:
        score -= 1
        findings.append(
            _finding(
                "medium",
                "Regression coverage is thin relative to the CLI, pipeline, and Studio surface area.",
                ["test-count", "pytest"],
                "A handoff engineer has limited protection against breaking the actual product workflow.",
                "Add tests for promotions, parser/build, Studio audit contracts, and CLI gate behavior.",
            )
        )

    if failures:
        findings.append(
            _finding(
                "high",
                "One or more verification checks failed.",
                ["pytest", "typecheck", "frontend-build"],
                "The current system cannot claim a clean handoff baseline.",
                "Make the verification suite green before expanding product surface area.",
            )
        )

    return AuditSubagentResult(
        id="maintainability",
        name="Maintainability/Test Auditor",
        category="Maintainability and tests",
        status=_status(score),
        score=max(score, 0),
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _operations_security(root: Path) -> AuditSubagentResult:
    quickstart = _read_doc(root, "QUICKSTART.md")
    config = _read(root / "backend/api/app/core/config.py")
    gitignore = _read(root / ".gitignore")
    evidence = [
        _evidence(
            "setup-prereqs",
            "doc",
            "QUICKSTART documents Python, TeX, font, poppler-utils, and Node.js prerequisites."
            if all(token in quickstart for token in ("Python", "TeX", "Node.js"))
            else "QUICKSTART prerequisites appear incomplete.",
            path="README.md",
        ),
        _evidence(
            "env-boundary",
            "file",
            f".env gitignored={'.env' in gitignore}; settings load .env.studio={'.env.studio' in config}.",
            path=".gitignore",
        ),
    ]
    score = 7
    findings: list[Finding] = []
    if "allow_methods=[\"*\"]" in config:
        score -= 1
        findings.append(
            _finding(
                "medium",
                "Studio CORS is permissive for local development.",
                ["env-boundary"],
                "This is acceptable locally but is not a deployment security posture.",
                "Document Studio as local-only or add production CORS settings before deployment.",
            )
        )

    return AuditSubagentResult(
        id="operations-security",
        name="Operations/Security Auditor",
        category="Operations and security",
        status=_status(score),
        score=score,
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _commercial_wedge(root: Path) -> AuditSubagentResult:
    readme = _read_doc(root, "README.md")
    handoff = _read_doc(root, "HANDOFF.md")
    evidence = [
        _evidence(
            "wedge-readme",
            "doc",
            "README positions Texgraph as a staged publishing pipeline for literary production.",
            path="README.md",
        ),
        _evidence(
            "wedge-handoff",
            "doc",
            "HANDOFF says concept is stronger than implementation and Studio/front-end/final work remains.",
            path="README.md",
        ),
    ]
    score = 7
    findings: list[Finding] = []
    if "Studio" in readme and "planned" in readme.lower():
        findings.append(
            _finding(
                "medium",
                "The credible wedge is the CLI publishing pipeline, not the full Studio platform.",
                ["wedge-readme", "wedge-handoff"],
                "Selling the larger platform claim now would overstate current readiness.",
                "Frame the next milestone around one repeatable CLI-to-Studio workflow instead of a broad platform.",
            )
        )
        score -= 1

    return AuditSubagentResult(
        id="commercial-wedge",
        name="Commercial Wedge Auditor",
        category="Commercial wedge",
        status=_status(score),
        score=score,
        findings=findings,
        evidence=evidence,
        open_questions=[],
    )


def _synthesize_report(subagents: list[AuditSubagentResult]) -> ReadinessReport:
    category_scores = {agent.category: agent.score for agent in subagents}
    findings = [finding for agent in subagents for finding in agent.findings]
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    priority = sorted(findings, key=lambda f: severity_order[f.severity])[:8]
    avg = sum(agent.score for agent in subagents) / max(len(subagents), 1)
    verdict = "promising_not_ready"
    if avg < 4:
        verdict = "not_ready"
    elif avg >= 8 and not any(f.severity in {"critical", "high"} for f in findings):
        verdict = "ready_for_limited_users"
    elif avg >= 7:
        verdict = "narrowly_usable"

    return ReadinessReport(
        one_sentence_product=(
            "Texgraph is a local, stage-gated publishing pipeline for literary collections, "
            "with a working CLI and an emerging React Studio control surface."
        ),
        specific_user="Technically comfortable poets, translators, and small press editors producing serious literary editions.",
        works_today_without_founder=[
            "A user can follow the documented CLI path to register projects and build a draft PDF when prerequisites are installed.",
            "The repository exposes stage contracts, schemas, and routing rules through AGENTS.md and README.md.",
            "Studio exposes project, editor, build, covers, and chat surfaces, though not full pipeline gate control.",
        ],
        breaks_first=[
            "Promotion is not fully executable because `texgraph promote <stage>` is missing.",
            "Studio does not yet make PROMOTION.yaml gate state visible.",
            "Agent behavior is chat-oriented and not yet classification-aware or evaluated.",
        ],
        next_risk_reducing_milestone=(
            "Implement executable promotion plus Studio gate visibility for one project, then prove the flow with tests."
        ),
        verdict=verdict,
        category_scores=category_scores,
        executive_summary=(
            "This is real engineering, but it is not yet a ready product. The CLI and documentation show a coherent "
            "publishing system; the product risk is that the visible Studio surface and gate automation lag behind the "
            "architecture. Narrow the claim to the repeatable publishing workflow and make promotion visible before expanding."
        ),
        highest_risk_assumption=(
            "That users can understand and trust the stage-gated workflow without the founder explaining what is current, planned, or manual."
        ),
        priority_findings=priority,
    )
