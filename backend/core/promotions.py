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

from backend.core.modules import get_module, load_modules, upstream_for

PROMOTION_FILENAME = "PROMOTION.yaml"

VALID_STAGES = tuple(module.id for module in load_modules())

# Maps each canonical module and legacy alias to the upstream module path whose
# PROMOTION.yaml it requires.
UPSTREAM: dict[str, str] = {}
for _module in load_modules():
    if _module.upstream:
        _upstream_paths = [get_module(upstream).path for upstream in _module.upstream]
        for _alias in _module.aliases:
            UPSTREAM[_alias] = ", ".join(_upstream_paths)

_STATUS_ORDER = ["not_started", "transcribed", "checked", "final"]


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def promotion_path(project_root: Path, stage: str) -> Path:
    """Return the promotion path for a canonical module or legacy alias."""
    module = get_module(stage)
    candidates = [project_root / module.path / PROMOTION_FILENAME]
    candidates.extend(project_root / alias / PROMOTION_FILENAME for alias in module.legacy_aliases)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    if (project_root / module.path).exists():
        return candidates[0]
    for alias in module.legacy_aliases:
        legacy_dir = project_root / alias
        if legacy_dir.exists():
            return legacy_dir / PROMOTION_FILENAME
    return candidates[0]


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
    try:
        module = get_module(stage)
    except KeyError:
        return False, [
            f"Stage '{stage}' has no upstream preconditions defined.",
            f"Valid stages with gates: {', '.join(UPSTREAM)}",
        ]

    upstream_modules = upstream_for(module.id)
    if not upstream_modules:
        return True, []

    issues: list[str] = []
    for upstream_module in upstream_modules:
        promo = read_promotion(project_root, upstream_module.id)

        if promo is None:
            issues.extend([
                f"{upstream_module.path}/PROMOTION.yaml not found.",
                f"Complete the {upstream_module.id} module, then run:  texgraph promote {upstream_module.id}",
            ])
            continue

        checker = _CHECKERS.get(upstream_module.id)
        if checker is not None:
            issues.extend(checker(promo, project_root))
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# Per-stage precondition checkers
# ---------------------------------------------------------------------------

def _check_ingest(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append(
            "sources/PROMOTION.yaml: status is not 'approved' — "
            "run: texgraph promote sources"
        )

    sources: list[dict[str, Any]] = promo.get("sources") or []
    if not sources:
        issues.append("sources/PROMOTION.yaml: no sources listed — run texgraph ingest rename first")
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
        issues.append("transcription/PROMOTION.yaml: status is not 'approved'")

    if not promo.get("policy_accepted"):
        issues.append("transcription/PROMOTION.yaml: policy_accepted is not true")

    volumes: list[dict[str, Any]] = promo.get("volumes") or []
    if not volumes:
        issues.append("transcription/PROMOTION.yaml: no volumes listed")
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
            "transcription/PROMOTION.yaml: uncertain_readings exist but "
            "uncertain_readings_accepted is not true — resolve or explicitly accept"
        )

    return issues


def _check_proof(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("manuscript/PROMOTION.yaml: status is not 'approved'")

    pdf = promo.get("proof_pdf")
    if not pdf:
        issues.append("manuscript/PROMOTION.yaml: proof_pdf is missing")
    elif not (project_root / pdf).exists():
        issues.append(f"manuscript/PROMOTION.yaml: proof_pdf not found on disk: {pdf}")

    tq = promo.get("textual_questions") or {}
    open_q = tq.get("open", -1)
    if open_q != 0:
        issues.append(
            f"manuscript/PROMOTION.yaml: textual_questions.open is {open_q} (must be 0 for promotion)"
        )

    pc = promo.get("page_count")
    if pc is not None and pc % 2 != 0:
        issues.append(
            f"manuscript/PROMOTION.yaml: page_count {pc} is odd — add a blank page to make it even"
        )

    if not promo.get("user_accepted_layout"):
        issues.append("manuscript/PROMOTION.yaml: user_accepted_layout is not true")

    return issues


def _check_typeset(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("interior/PROMOTION.yaml: status is not 'approved'")

    pdf = promo.get("interior_pdf")
    if not pdf:
        issues.append("interior/PROMOTION.yaml: interior_pdf is missing")
    elif not (project_root / pdf).exists():
        issues.append(f"interior/PROMOTION.yaml: interior_pdf not found on disk: {pdf}")

    if not promo.get("fonts_embedded"):
        issues.append(
            "interior/PROMOTION.yaml: fonts_embedded is not true — "
            "verify with: pdffonts <interior_pdf>"
        )

    if not promo.get("user_approved_interior"):
        issues.append("interior/PROMOTION.yaml: user_approved_interior is not true")

    return issues


def _check_final(promo: dict[str, Any], project_root: Path) -> list[str]:
    issues: list[str] = []

    if promo.get("status") != "approved":
        issues.append("release/PROMOTION.yaml: status is not 'approved'")

    pdf = promo.get("final_pdf")
    if not pdf:
        issues.append("release/PROMOTION.yaml: final_pdf is missing")
    elif not (project_root / pdf).exists():
        issues.append(f"release/PROMOTION.yaml: final_pdf not found on disk: {pdf}")

    return issues


_CHECKERS: dict[str, Any] = {
    "sources": _check_ingest,
    "transcription": _check_transcribe,
    "manuscript": _check_proof,
    "interior": _check_typeset,
    "release": _check_final,
}
