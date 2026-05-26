"""Stage promotion records — PROMOTION.yaml read, write, and verify.

A PROMOTION.yaml file at ``projects/<id>/<stage>/PROMOTION.yaml`` is the
machine-readable gate between pipeline stages.  A stage may not begin until
the upstream stage's PROMOTION.yaml exists and passes verification.

Typical flow
------------
1. Complete stage work.
2. ``texgraph verify <next_stage>`` — checks upstream PROMOTION.yaml.
3. ``texgraph promote <stage>`` — user approves; writes PROMOTION.yaml.
4. Next stage is now unlocked.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROMOTION_FILENAME = "PROMOTION.yaml"

VALID_STAGES = ("ingest", "transcribe", "proof", "typeset", "covers", "front-end", "final")

# Maps each stage to the upstream stage whose PROMOTION.yaml it requires.
UPSTREAM: dict[str, str] = {
    "transcribe": "ingest",
    "proof": "transcribe",
    "typeset": "proof",
    "final": "typeset",
    "covers": "final",
}

_STATUS_ORDER = ["not_started", "transcribed", "checked", "final"]


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def promotion_path(project_root: Path, stage: str) -> Path:
    """Return the path to ``<stage>/PROMOTION.yaml`` within *project_root*."""
    return project_root / stage / PROMOTION_FILENAME


def read_promotion(project_root: Path, stage: str) -> dict[str, Any] | None:
    """Read and parse a PROMOTION.yaml, or return None if absent."""
    path = promotion_path(project_root, stage)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def write_promotion(project_root: Path, stage: str, data: dict[str, Any]) -> Path:
    """Write *data* to ``<stage>/PROMOTION.yaml``, creating the directory if needed."""
    path = promotion_path(project_root, stage)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return path


# ---------------------------------------------------------------------------
# Verification entry point
# ---------------------------------------------------------------------------

def verify_stage(project_root: Path, stage: str) -> tuple[bool, list[str]]:
    """Check that the upstream PROMOTION.yaml satisfies *stage*'s preconditions.

    Parameters
    ----------
    project_root:
        Absolute path to the project's stage root (``projects/<id>/``).
    stage:
        The stage about to begin — verified against its upstream.

    Returns
    -------
    (ok, issues)
        *ok* is True when all preconditions pass.  *issues* contains
        human-readable failure messages when *ok* is False.
    """
    if stage not in UPSTREAM:
        return False, [
            f"Stage '{stage}' has no upstream preconditions defined.",
            f"Valid stages with gates: {', '.join(UPSTREAM)}",
        ]

    upstream = UPSTREAM[stage]
    promo = read_promotion(project_root, upstream)

    if promo is None:
        return False, [
            f"{upstream}/PROMOTION.yaml not found.",
            f"Complete the {upstream} stage, then run:  texgraph promote {upstream}",
        ]

    checker = _CHECKERS.get(upstream)
    if checker is None:
        return True, []

    issues = checker(promo, project_root)
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# Per-stage precondition checkers
# ---------------------------------------------------------------------------

def _check_ingest(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append(
            "ingest/PROMOTION.yaml: status is not 'approved' — "
            "run: texgraph promote ingest"
        )

    sources: list[dict[str, Any]] = promo.get("sources") or []
    if not sources:
        issues.append("ingest/PROMOTION.yaml: no sources listed — run texgraph ingest rename first")
        return issues

    for s in sources:
        name = s.get("stable_name", "(unnamed)")
        if not s.get("access_confirmed"):
            issues.append(f"  source '{name}': access_confirmed is not true")
        sp = s.get("stable_path")
        if sp:
            if not (project_root / sp).exists():
                issues.append(f"  source '{name}': stable_path not found on disk: {sp}")
        else:
            issues.append(f"  source '{name}': stable_path is missing")

    return issues


def _check_transcribe(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("transcribe/PROMOTION.yaml: status is not 'approved'")

    if not promo.get("policy_accepted"):
        issues.append("transcribe/PROMOTION.yaml: policy_accepted is not true")

    volumes: list[dict[str, Any]] = promo.get("volumes") or []
    if not volumes:
        issues.append("transcribe/PROMOTION.yaml: no volumes listed")
        return issues

    floor = promo.get("all_statuses_at_least", "transcribed")
    floor_idx = _STATUS_ORDER.index(floor) if floor in _STATUS_ORDER else 1

    for v in volumes:
        vid = v.get("id", "?")
        vstatus = v.get("transcription_status", "not_started")
        vstatus_idx = _STATUS_ORDER.index(vstatus) if vstatus in _STATUS_ORDER else 0
        if vstatus_idx < floor_idx:
            issues.append(
                f"  volume '{vid}': transcription_status '{vstatus}' "
                f"is below required floor '{floor}'"
            )

    has_open_readings = any(
        len(v.get("uncertain_readings") or []) > 0 for v in volumes
    )
    if has_open_readings and not promo.get("uncertain_readings_accepted"):
        issues.append(
            "transcribe/PROMOTION.yaml: uncertain_readings exist but "
            "uncertain_readings_accepted is not true — resolve or explicitly accept"
        )

    return issues


def _check_proof(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("proof/PROMOTION.yaml: status is not 'approved'")

    pdf = promo.get("proof_pdf")
    if not pdf:
        issues.append("proof/PROMOTION.yaml: proof_pdf is missing")
    elif not (project_root / pdf).exists():
        issues.append(f"proof/PROMOTION.yaml: proof_pdf not found on disk: {pdf}")

    tq = promo.get("textual_questions") or {}
    open_q = tq.get("open", -1)
    if open_q != 0:
        issues.append(
            f"proof/PROMOTION.yaml: textual_questions.open is {open_q} (must be 0 for promotion)"
        )

    pc = promo.get("page_count")
    if pc is not None and pc % 2 != 0:
        issues.append(
            f"proof/PROMOTION.yaml: page_count {pc} is odd — add a blank page to make it even"
        )

    if not promo.get("user_accepted_layout"):
        issues.append("proof/PROMOTION.yaml: user_accepted_layout is not true")

    return issues


def _check_typeset(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("typeset/PROMOTION.yaml: status is not 'approved'")

    pdf = promo.get("interior_pdf")
    if not pdf:
        issues.append("typeset/PROMOTION.yaml: interior_pdf is missing")
    elif not (project_root / pdf).exists():
        issues.append(f"typeset/PROMOTION.yaml: interior_pdf not found on disk: {pdf}")

    if not promo.get("fonts_embedded"):
        issues.append(
            "typeset/PROMOTION.yaml: fonts_embedded is not true — "
            "verify with: pdffonts <interior_pdf>"
        )

    if not promo.get("user_approved_interior"):
        issues.append("typeset/PROMOTION.yaml: user_approved_interior is not true")

    return issues


def _check_final(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("final/PROMOTION.yaml: status is not 'approved'")

    pdf = promo.get("final_pdf")
    if not pdf:
        issues.append("final/PROMOTION.yaml: final_pdf is missing")
    elif not (project_root / pdf).exists():
        issues.append(f"final/PROMOTION.yaml: final_pdf not found on disk: {pdf}")

    cu = promo.get("cover_unlock") or {}
    if not cu.get("unlocked"):
        issues.append("final/PROMOTION.yaml: cover_unlock.unlocked is not true")

    return issues


_CHECKERS: dict[str, Any] = {
    "ingest": _check_ingest,
    "transcribe": _check_transcribe,
    "proof": _check_proof,
    "typeset": _check_typeset,
    "final": _check_final,
}
