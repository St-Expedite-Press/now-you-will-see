"""Project and workspace CRUD operations.

Reads/writes workspace.yaml and per-project collection.yaml using
the existing texgraph.config and texgraph.workspace modules.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.project import CollectionMeta, ProjectCreate, ProjectDetail, ProjectRef, WorkspaceInfo

SEMANTIC_MODULE_DIRS = (
    "sources",
    "transcription",
    "manuscript",
    "interior",
    "covers",
    "publication",
    "release",
)

LEGACY_STAGE_ALIASES = {
    "ingest": "sources",
    "transcribe": "transcription",
    "typeset": "interior",
    "front-end": "publication",
    "final": "release",
}

# Add src/ to path so texgraph package is importable from the Studio backend
_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def _workspace_path() -> Path:
    return settings.workspace_root / "workspace.yaml"


def get_workspace() -> WorkspaceInfo:
    from backend.core.workspace import find_workspace, load_workspace

    ws_path = find_workspace(settings.workspace_root)
    if ws_path is None:
        raise NotFoundError("workspace.yaml not found")
    ws = load_workspace(ws_path)
    refs = [ProjectRef(id=p.id, path=p.path, description=p.description) for p in ws.list_projects()]
    return WorkspaceInfo(
        workspace_path=str(ws_path),
        default_project=ws.default_project,
        projects=refs,
    )


def get_project(project_id: str) -> ProjectDetail:
    from backend.core.config import CollectionConfig
    from backend.core.workspace import find_workspace, load_workspace, resolve_project

    ws_path = find_workspace(settings.workspace_root)
    if ws_path is None:
        raise NotFoundError("workspace.yaml not found")
    ws = load_workspace(ws_path)
    try:
        cfg = resolve_project(ws, project_id)
    except (KeyError, ValueError) as exc:
        raise NotFoundError(str(exc)) from exc

    return _cfg_to_detail(project_id, cfg)


def create_project(body: ProjectCreate) -> ProjectDetail:
    from backend.core.workspace import find_workspace, load_workspace

    ws_path = find_workspace(settings.workspace_root)
    if ws_path is None:
        raise NotFoundError("workspace.yaml not found")
    ws = load_workspace(ws_path)
    for ref in ws.list_projects():
        if ref.id == body.id:
            raise ConflictError(f"Project '{body.id}' already exists")

    normalized_path, project_dir = _resolve_new_project_dir(body.path)
    for ref in ws.list_projects():
        existing_dir = (settings.workspace_root / ref.path).resolve()
        if existing_dir == project_dir:
            raise ConflictError(f"Project path '{normalized_path}' is already in use by '{ref.id}'")

    if project_dir.exists():
        if not project_dir.is_dir():
            raise ConflictError(f"Project path '{normalized_path}' already exists and is not a directory")
        if any(project_dir.iterdir()):
            raise ConflictError(f"Project path '{normalized_path}' already exists and is not empty")
    else:
        project_dir.mkdir(parents=True, exist_ok=False)

    _ensure_project_stage_dirs(project_dir)
    _write_collection_yaml(project_dir, body.meta)

    # Append to workspace.yaml
    import yaml
    with ws_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    data.setdefault("projects", []).append({
        "id": body.id,
        "path": normalized_path,
        "description": body.description,
    })
    with ws_path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, sort_keys=False)

    return get_project(body.id)


# --- Private helpers ---

def _resolve_new_project_dir(raw_path: str) -> tuple[str, Path]:
    candidate = Path(raw_path.strip())
    if not raw_path.strip():
        raise ValidationError("Project path is required")
    if candidate.is_absolute():
        raise ValidationError("Project path must be relative to the workspace root")

    workspace_root = settings.workspace_root.resolve()
    project_dir = (workspace_root / candidate).resolve()
    if project_dir == workspace_root or workspace_root not in project_dir.parents:
        raise ValidationError("Project path must stay inside the workspace root")

    try:
        normalized = project_dir.relative_to(workspace_root).as_posix()
    except ValueError as exc:
        raise ValidationError("Project path must stay inside the workspace root") from exc

    if normalized in {"", "."}:
        raise ValidationError("Project path must resolve to a project directory")

    return normalized, project_dir

def _write_collection_yaml(project_dir: Path, meta: CollectionMeta) -> None:
    import yaml
    content_dir = project_dir / meta.content_dir
    output_dir = project_dir / meta.output_dir
    content_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    data = meta.model_dump(exclude_none=True)
    with (project_dir / "collection.yaml").open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, sort_keys=False)


def _ensure_project_stage_dirs(project_dir: Path) -> None:
    """Create semantic module folders plus legacy aliases where needed."""
    if project_dir.name not in {"interior", "typeset"}:
        project_root = project_dir
    else:
        project_root = project_dir.parent

    for dirname in SEMANTIC_MODULE_DIRS:
        (project_root / dirname).mkdir(parents=True, exist_ok=True)

    for legacy_dir, semantic_dir in LEGACY_STAGE_ALIASES.items():
        if legacy_dir == "typeset" and project_dir.name == "typeset":
            continue
        legacy_path = project_root / legacy_dir
        semantic_path = project_root / semantic_dir
        if legacy_path.exists():
            continue
        try:
            legacy_path.symlink_to(semantic_path, target_is_directory=True)
        except OSError:
            legacy_path.mkdir(parents=True, exist_ok=True)


def _cfg_to_detail(project_id: str, cfg: object) -> ProjectDetail:
    from backend.core.parser import PoetryParser

    meta = CollectionMeta(
        title=getattr(cfg, "title", ""),
        author=getattr(cfg, "author", ""),
        subtitle=getattr(cfg, "subtitle", "") or "",
        year=getattr(cfg, "year", None),
        publisher=getattr(cfg, "publisher", "") or "",
        isbn=getattr(cfg, "isbn", "") or "",
        content_dir=getattr(cfg, "content_dir", "content"),
        output_dir=getattr(cfg, "output_dir", "output"),
        lualatex_path=getattr(cfg, "lualatex_path", "lualatex"),
        draft_mode=getattr(cfg, "draft_mode", False),
    )
    section_count = 0
    poem_count = 0
    last_built: str | None = None
    try:
        parser = PoetryParser()
        sections = parser.scan_collection(getattr(cfg, "resolved_content_dir", Path("content")))
        section_count = len(sections)
        poem_count = sum(len(s.poems) for s in sections)
    except Exception:
        pass
    try:
        output_dir = Path(getattr(cfg, "project_root", "")) / getattr(cfg, "output_dir", "output")
        state_path = output_dir / ".studio-build-state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if state.get("status") == "success":
                last_built = str(state.get("finished_at") or state.get("started_at") or "")
    except Exception:
        last_built = None

    return ProjectDetail(
        id=project_id,
        path=str(getattr(cfg, "project_root", "")),
        meta=meta,
        section_count=section_count,
        poem_count=poem_count,
        last_built=last_built or None,
    )

