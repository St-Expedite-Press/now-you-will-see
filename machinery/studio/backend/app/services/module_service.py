"""Semantic module lookup and gate verification for Studio projects."""

from __future__ import annotations

import sys
from pathlib import Path

from app.core.exceptions import NotFoundError
from app.models.module import ModuleVerifyResult, ProjectModule, ProjectModuleList
from app.services import project_service

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def list_modules(project_id: str) -> ProjectModuleList:
    detail = project_service.get_project(project_id)
    project_root = _artifact_root(Path(detail.path))
    from texgraph.modules import load_modules

    modules = [_spec_to_module(project_root, Path(detail.path), spec) for spec in load_modules()]
    return ProjectModuleList(project_id=project_id, modules=modules)


def get_module(project_id: str, module_id: str) -> ProjectModule:
    detail = project_service.get_project(project_id)
    spec = _get_spec(module_id)
    return _spec_to_module(_artifact_root(Path(detail.path)), Path(detail.path), spec)


def verify_module(project_id: str, module_id: str) -> ModuleVerifyResult:
    detail = project_service.get_project(project_id)
    spec = _get_spec(module_id)
    module = _spec_to_module(_artifact_root(Path(detail.path)), Path(detail.path), spec)
    project_root = _artifact_root(Path(detail.path))

    if not spec.upstream:
        exists = Path(module.path).exists()
        return ModuleVerifyResult(
            project_id=project_id,
            module_id=module_id,
            ok=exists,
            status="present" if exists else "missing",
            verify_stage=None,
            checked_path=module.path,
            issues=[] if exists else [f"{module.path} does not exist."],
        )

    from texgraph.promotions import verify_stage

    ok, issues = verify_stage(project_root, spec.id)
    return ModuleVerifyResult(
        project_id=project_id,
        module_id=module_id,
        ok=ok,
        status="ready" if ok else "blocked",
        verify_stage=spec.id,
        checked_path=str(project_root),
        issues=issues,
    )


def _get_spec(module_id: str):
    from texgraph.modules import resolve_module

    try:
        return resolve_module(module_id)
    except KeyError as exc:
        raise NotFoundError(f"Module '{module_id}' not found") from exc


def _artifact_root(interior_root: Path) -> Path:
    if interior_root.name in {"interior", "typeset"}:
        return interior_root.parent
    return interior_root


def _module_path(project_root: Path, interior_root: Path, spec) -> Path:
    if spec.id == "interior":
        return interior_root
    semantic = project_root / spec.path
    legacy = project_root / spec.legacy_aliases[0] if spec.legacy_aliases else None
    if semantic.exists() or legacy is None or not legacy.exists():
        return semantic
    return legacy


def _spec_to_module(project_root: Path, interior_root: Path, spec) -> ProjectModule:
    path = _module_path(project_root, interior_root, spec)
    legacy_stage = spec.legacy_aliases[0] if spec.legacy_aliases else None
    legacy_path = str(project_root / legacy_stage) if legacy_stage else None
    return ProjectModule(
        id=spec.id,
        label=spec.label,
        description=spec.description,
        path=str(path),
        exists=path.exists(),
        legacy_stage=legacy_stage,
        legacy_path=legacy_path,
        workspace_alias=spec.id == "interior",
        verify_stage=spec.id if spec.upstream else None,
    )
