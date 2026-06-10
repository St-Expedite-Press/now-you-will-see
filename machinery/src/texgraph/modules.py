"""Canonical pipeline module registry and project module migration helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from texgraph.env import repo_root
from texgraph.workspace import find_workspace, load_workspace


MODULE_MANIFEST = "module.yaml"


@dataclass(frozen=True)
class ModuleDef:
    """A canonical pipeline module definition."""

    id: str
    label: str
    path: str
    artifact_path: str | None = None
    legacy_aliases: tuple[str, ...] = field(default_factory=tuple)
    upstream: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""
    source: str = "builtin"

    @property
    def aliases(self) -> tuple[str, ...]:
        return (self.id, *self.legacy_aliases)


CANONICAL_MODULES: tuple[str, ...] = (
    "workspace",
    "sources",
    "transcription",
    "manuscript",
    "interior",
    "covers",
    "publication",
    "release",
)


BUILTIN_MODULES: tuple[ModuleDef, ...] = (
    ModuleDef(
        id="workspace",
        label="Workspace",
        path="workspace",
        description="Project registration and workspace-level configuration.",
    ),
    ModuleDef(
        id="sources",
        label="Sources",
        path="sources",
        legacy_aliases=("ingest",),
        description="Source intake, raw files, provenance, and source promotion.",
    ),
    ModuleDef(
        id="transcription",
        label="Transcription",
        path="transcription",
        legacy_aliases=("transcribe",),
        upstream=("sources",),
        description="Transcribed text, plans, and transcription promotion.",
    ),
    ModuleDef(
        id="manuscript",
        label="Manuscript",
        path="manuscript",
        legacy_aliases=("proof",),
        upstream=("transcription",),
        description="Proof/manuscript review records and draft-readiness checks.",
    ),
    ModuleDef(
        id="interior",
        label="Interior",
        path="interior",
        legacy_aliases=("typeset",),
        upstream=("transcription",),
        description="Collection source, layout, proof drafts, and interior PDFs.",
    ),
    ModuleDef(
        id="covers",
        label="Covers",
        path="covers",
        upstream=("interior",),
        description="Cover assets and cover production.",
    ),
    ModuleDef(
        id="publication",
        label="Publication",
        path="publication",
        legacy_aliases=("front-end", "frontend"),
        upstream=("interior",),
        description="E-reader, web, and publication-facing output.",
    ),
    ModuleDef(
        id="release",
        label="Release",
        path="release",
        legacy_aliases=("final",),
        upstream=("interior",),
        description="Release packages, manifests, and delivery artifacts.",
    ),
)

LEGACY_MODULE_MIGRATION: dict[str, str] = {
    "ingest": "sources",
    "transcribe": "transcription",
    "proof": "manuscript",
    "typeset": "interior",
    "front-end": "publication",
    "final": "release",
    "covers": "covers",
}


def load_modules(root: Path | None = None) -> list[ModuleDef]:
    """Load canonical modules from ``modules/*/module.yaml`` with built-in fallback."""

    base = (root or repo_root()).resolve()
    modules_by_id = {module.id: module for module in BUILTIN_MODULES}
    manifests_root = base / "modules"

    if manifests_root.is_dir():
        for manifest in sorted(manifests_root.glob(f"*/{MODULE_MANIFEST}")):
            data = _read_manifest(manifest)
            module = _module_from_manifest(data, manifest)
            if module is not None:
                modules_by_id[module.id] = module

    return [modules_by_id[module_id] for module_id in CANONICAL_MODULES if module_id in modules_by_id] + [
        module
        for module_id, module in sorted(modules_by_id.items())
        if module_id not in set(CANONICAL_MODULES)
    ]


def get_module(name: str, root: Path | None = None) -> ModuleDef:
    """Resolve a canonical module id or legacy alias to a module definition."""

    normalized = _normalize(name)
    for module in load_modules(root):
        if normalized in {_normalize(alias) for alias in module.aliases}:
            return module
    valid = ", ".join(module.id for module in load_modules(root))
    raise KeyError(f"Unknown module or alias '{name}'. Valid modules: {valid}")


def resolve_module(name: str, root: Path | None = None) -> str:
    """Resolve a module id or legacy alias to a canonical module id."""

    if is_legacy_support(name):
        raise ValueError(f"'{name}' is a legacy support directory, not a pipeline module")
    return get_module(name, root).id


def module_path(name: str, root: Path | None = None) -> Path:
    """Return the canonical artifact path for a module."""

    module = get_module(name, root)
    return Path(module.path)


def is_legacy_support(name: str) -> bool:
    return _normalize(name) == "proof"


def valid_module_aliases(root: Path | None = None) -> list[str]:
    """Return all canonical module ids and legacy aliases."""

    aliases: list[str] = []
    for module in load_modules(root):
        aliases.extend(module.aliases)
    return aliases


def upstream_for(name: str, root: Path | None = None) -> list[ModuleDef]:
    """Return upstream modules required before *name*."""

    module = get_module(name, root)
    return [get_module(upstream, root) for upstream in module.upstream]


@dataclass(frozen=True)
class ModuleMigrationStep:
    old_name: str
    new_name: str
    old_path: Path
    new_path: Path
    action: str
    reason: str = ""


@dataclass(frozen=True)
class ModuleMigrationPlan:
    project_id: str
    project_root: Path
    workspace_path: Path
    workspace_project_path: str
    updated_workspace_project_path: str
    steps: tuple[ModuleMigrationStep, ...]
    conflicts: tuple[str, ...]

    @property
    def has_changes(self) -> bool:
        return any(step.action == "move" for step in self.steps) or (
            self.workspace_project_path != self.updated_workspace_project_path
        )


def plan_module_migration(project_id: str, start: Path | None = None) -> ModuleMigrationPlan:
    """Plan old stage directory names to canonical module directory names."""

    workspace_path = find_workspace(start or Path.cwd())
    if workspace_path is None:
        raise FileNotFoundError("No workspace.yaml found.")

    workspace = load_workspace(workspace_path)
    ref = workspace.get_project(project_id)
    ref_abs = (workspace.workspace_root / ref.path).resolve()
    project_root = _project_root_from_ref(ref_abs)

    steps: list[ModuleMigrationStep] = []
    conflicts: list[str] = []
    for old_name, new_name in LEGACY_MODULE_MIGRATION.items():
        old_path = project_root / old_name
        new_path = project_root / new_name
        if old_name == new_name:
            action = "keep" if old_path.exists() else "missing"
            steps.append(ModuleMigrationStep(old_name, new_name, old_path, new_path, action))
            continue
        if old_path.exists() and new_path.exists():
            msg = f"both {old_name}/ and {new_name}/ exist"
            conflicts.append(msg)
            steps.append(ModuleMigrationStep(old_name, new_name, old_path, new_path, "conflict", msg))
        elif old_path.exists():
            steps.append(ModuleMigrationStep(old_name, new_name, old_path, new_path, "move"))
        elif new_path.exists():
            steps.append(ModuleMigrationStep(old_name, new_name, old_path, new_path, "already"))
        else:
            steps.append(ModuleMigrationStep(old_name, new_name, old_path, new_path, "missing"))

    updated_path = _updated_workspace_path(ref.path)
    return ModuleMigrationPlan(
        project_id=project_id,
        project_root=project_root,
        workspace_path=workspace_path,
        workspace_project_path=ref.path,
        updated_workspace_project_path=updated_path,
        steps=tuple(steps),
        conflicts=tuple(conflicts),
    )


def apply_module_migration(plan: ModuleMigrationPlan) -> None:
    """Apply a conflict-free module migration plan."""

    if plan.conflicts:
        joined = "; ".join(plan.conflicts)
        raise RuntimeError(f"Refusing migration due to conflicts: {joined}")

    for step in plan.steps:
        if step.action == "move":
            step.new_path.parent.mkdir(parents=True, exist_ok=True)
            step.old_path.rename(step.new_path)

    if plan.workspace_project_path != plan.updated_workspace_project_path:
        _rewrite_workspace_project_path(
            plan.workspace_path,
            plan.project_id,
            plan.updated_workspace_project_path,
        )


def _read_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _module_from_manifest(data: dict[str, Any], manifest: Path) -> ModuleDef | None:
    module_id = str(data.get("id") or manifest.parent.name).strip()
    if not module_id:
        return None
    builtin = next((item for item in BUILTIN_MODULES if item.id == module_id), None)
    manifest_aliases = data.get("legacy_aliases") or data.get("legacy_ids") or data.get("aliases") or ()
    aliases = tuple(dict.fromkeys(
        [*(builtin.legacy_aliases if builtin else ()), *(str(alias) for alias in manifest_aliases)]
    ))
    raw_upstream = data.get("upstream")
    if isinstance(raw_upstream, list):
        upstream = tuple(str(item) for item in raw_upstream)
    elif raw_upstream:
        upstream = (str(raw_upstream),)
    else:
        upstream = builtin.upstream if builtin else ()
    artifact_dir = str(data.get("artifact_dir") or "")
    artifact_path = None
    if artifact_dir:
        marker = "projects/<project_id>/"
        artifact_path = artifact_dir.split(marker, 1)[1] if marker in artifact_dir else artifact_dir
    return ModuleDef(
        id=module_id,
        label=str(data.get("label") or (builtin.label if builtin else module_id.replace("-", " ").title())),
        path=str(data.get("path") or (builtin.path if builtin else module_id)),
        artifact_path=artifact_path or (builtin.artifact_path if builtin else None),
        legacy_aliases=aliases,
        upstream=upstream,
        description=str(data.get("description") or (builtin.description if builtin else "")),
        source=str(manifest),
    )


def _normalize(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def _project_root_from_ref(ref_path: Path) -> Path:
    if ref_path.name in {module.path for module in load_modules()} or ref_path.name in LEGACY_MODULE_MIGRATION:
        return ref_path.parent
    return ref_path


def _updated_workspace_path(path: str) -> str:
    parts = Path(path).parts
    if not parts:
        return path
    new_name = LEGACY_MODULE_MIGRATION.get(parts[-1])
    if new_name:
        return str(Path(*parts[:-1], new_name)).replace("\\", "/")
    return path


def _rewrite_workspace_project_path(workspace_path: Path, project_id: str, new_path: str) -> None:
    data = _read_manifest(workspace_path)
    projects = data.get("projects") or []
    for entry in projects:
        if isinstance(entry, dict) and str(entry.get("id")) == project_id:
            entry["path"] = new_path
            break
    with workspace_path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)
