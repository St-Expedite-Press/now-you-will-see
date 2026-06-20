"""
Configuration loader for Texgraph.

Reads ``collection.yaml`` for book-level metadata and optionally merges
environment variables from ``.env.texgraph`` (via python-dotenv) so that
sensitive or machine-specific paths (e.g. lualatex binary location) can be
kept out of version control.

Also provides :class:`WorkspaceConfig` and :class:`ProjectRef` for
multi-project workspace support via ``workspace.yaml``.

Usage::

    config = CollectionConfig.from_yaml("collection.yaml")

    workspace = WorkspaceConfig.from_yaml(Path("workspace.yaml"))
    config = workspace.get_collection_config("my-project")
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_env(project_root: Path) -> None:
    """Load ``.env.texgraph`` from *project_root* if it exists."""
    env_file = project_root / ".env.texgraph"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read and parse a YAML file, returning an empty dict on missing file."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _as_bool(value: Any) -> bool:
    """Coerce common YAML/env representations to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    return bool(value)


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class CollectionConfig:
    """All configuration for a single poetry-collection build.

    Attributes
    ----------
    title:
        Full title of the collection (required).
    subtitle:
        Optional subtitle printed below the main title.
    author:
        Author name as it should appear on the cover and copyright page.
    year:
        Publication year (four-digit integer, e.g. 2025).
    publisher:
        Publisher name for the copyright notice.
    isbn:
        ISBN-13 string (hyphens optional, e.g. ``"978-0-000-00000-0"``).
    language:
        BCP-47 language tag used for ``babel``/``polyglossia`` (default ``"en"``).
    lualatex_path:
        Filesystem path (or bare command name) of the ``lualatex`` binary.
        Defaults to ``"lualatex"`` which works when TeX Live is on ``PATH``.
    output_dir:
        Directory where compiled PDFs and intermediate ``.tex`` files are
        written.  Relative paths are resolved from the project root.
    content_dir:
        Root directory that contains section sub-directories and ``.md`` poem
        files.  Relative paths are resolved from the project root.
    draft_mode:
        When ``True``, lualatex is run only once and PDF/X metadata is not
        injected, which speeds up iteration.
    project_root:
        Resolved root directory of the project (set automatically).
    """

    title: str
    author: str
    subtitle: str = ""
    year: int = 2025
    publisher: str = ""
    isbn: str = ""
    language: str = "en"
    lualatex_path: str = "lualatex"
    output_dir: str = "output"
    content_dir: str = "content"
    draft_mode: bool = False
    render_config: dict[str, Any] = field(default_factory=dict)
    project_root: Path = field(default_factory=Path.cwd)

    # ------------------------------------------------------------------
    # Derived paths
    # ------------------------------------------------------------------

    @property
    def resolved_output_dir(self) -> Path:
        """Absolute path to the output directory."""
        p = Path(self.output_dir)
        return p if p.is_absolute() else self.project_root / p

    @property
    def resolved_content_dir(self) -> Path:
        """Absolute path to the content directory."""
        p = Path(self.content_dir)
        return p if p.is_absolute() else self.project_root / p

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(
        cls,
        yaml_path: str | Path = "collection.yaml",
        *,
        load_dotenv_file: bool = True,
    ) -> "CollectionConfig":
        """Create a :class:`CollectionConfig` from *yaml_path*.

        Environment variables (from ``.env.texgraph``) are merged **after**
        the YAML is parsed, meaning env-vars take precedence for path and
        toolchain settings.

        Parameters
        ----------
        yaml_path:
            Path to ``collection.yaml``.  Relative paths are resolved from
            the current working directory.
        load_dotenv_file:
            Whether to attempt loading ``.env.texgraph`` from the same
            directory as *yaml_path*.
        """
        yaml_path = Path(yaml_path).resolve()
        project_root = yaml_path.parent

        if load_dotenv_file:
            _load_env(project_root)

        data = _read_yaml(yaml_path)

        # Mandatory fields ----------------------------------------------------
        title = str(data.get("title") or os.environ.get("TEXGRAPH_TITLE") or "")
        author = str(data.get("author") or os.environ.get("TEXGRAPH_AUTHOR") or "")

        if not title:
            raise ValueError(
                f"'title' is required in {yaml_path} (or set TEXGRAPH_TITLE env var)"
            )
        if not author:
            raise ValueError(
                f"'author' is required in {yaml_path} (or set TEXGRAPH_AUTHOR env var)"
            )

        # Optional fields — env vars override YAML ---------------------------
        def _get(key: str, yaml_key: str | None = None, default: Any = "") -> Any:
            env_key = f"TEXGRAPH_{key.upper()}"
            return os.environ.get(env_key) or data.get(yaml_key or key, default)

        return cls(
            title=title,
            author=author,
            subtitle=str(_get("subtitle", default="")),
            year=int(_get("year", default=2025)),
            publisher=str(_get("publisher", default="")),
            isbn=str(_get("isbn", default="")),
            language=str(_get("language", default="en")),
            lualatex_path=str(_get("lualatex_path", "lualatex_path", default="lualatex")),
            output_dir=str(_get("output_dir", "output_dir", default="output")),
            content_dir=str(_get("content_dir", "content_dir", default="content")),
            draft_mode=_as_bool(_get("draft_mode", "draft_mode", default=False)),
            render_config=dict(data.get("render_config") or {}),
            project_root=project_root,
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def ensure_output_dir(self) -> Path:
        """Create the output directory if it does not exist and return it."""
        out = self.resolved_output_dir
        out.mkdir(parents=True, exist_ok=True)
        return out

    def as_dict(self) -> dict[str, Any]:
        """Return a plain dict suitable for passing to Jinja2 templates."""
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "author": self.author,
            "year": self.year,
            "publisher": self.publisher,
            "isbn": self.isbn,
            "language": self.language,
            "draft_mode": self.draft_mode,
            "render_config": dict(self.render_config),
        }


# ---------------------------------------------------------------------------
# Workspace dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ProjectRef:
    """Reference to a single project within a workspace.

    Attributes
    ----------
    id:
        Unique identifier for the project (used with ``--project``).
    path:
        Path to the project directory, relative to the workspace root.
    description:
        Optional human-readable description shown in ``texgraph list``.
    """

    id: str
    path: str
    description: str = ""


@dataclass
class WorkspaceConfig:
    """Configuration for a multi-project Texgraph workspace.

    Loaded from ``workspace.yaml`` at the workspace root.

    Attributes
    ----------
    workspace_root:
        Absolute path to the directory containing ``workspace.yaml``.
    projects:
        All projects declared in ``workspace.yaml``.
    default_project:
        ID of the project used when ``--project`` is not specified.
    """

    workspace_root: Path
    projects: list[ProjectRef]
    default_project: str = ""

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(cls, workspace_yaml: Path) -> "WorkspaceConfig":
        """Create a :class:`WorkspaceConfig` from *workspace_yaml*.

        Parameters
        ----------
        workspace_yaml:
            Path to ``workspace.yaml``.  Relative paths are resolved from
            the current working directory.
        """
        workspace_yaml = Path(workspace_yaml).resolve()
        workspace_root = workspace_yaml.parent

        data = _read_yaml(workspace_yaml)

        raw_projects: list[dict[str, Any]] = data.get("projects", [])
        projects: list[ProjectRef] = []
        for entry in raw_projects:
            if not isinstance(entry, dict):
                continue
            project_id = str(entry.get("id", ""))
            project_path = str(entry.get("path", ""))
            description = str(entry.get("description", ""))
            if not project_id or not project_path:
                raise ValueError(
                    f"Each project entry in {workspace_yaml} must have 'id' and 'path'."
                )
            projects.append(ProjectRef(id=project_id, path=project_path, description=description))

        default_project = str(data.get("default_project", ""))

        return cls(
            workspace_root=workspace_root,
            projects=projects,
            default_project=default_project,
        )

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def get_project(self, project_id: str) -> ProjectRef:
        """Return the :class:`ProjectRef` for *project_id*.

        Raises
        ------
        KeyError
            If no project with *project_id* exists in the workspace.
        """
        for project in self.projects:
            if project.id == project_id:
                return project
        available = ", ".join(p.id for p in self.projects)
        raise KeyError(
            f"Project '{project_id}' not found in workspace. "
            f"Available: {available or '(none)'}"
        )

    def get_collection_config(self, project_id: str) -> "CollectionConfig":
        """Load the :class:`CollectionConfig` for *project_id*.

        Resolves the project directory relative to :attr:`workspace_root`,
        then reads ``collection.yaml`` inside that directory. During the
        module migration window, ``path`` may point at either the canonical
        ``interior`` module root, the legacy ``typeset`` root, or the project
        root itself.

        Parameters
        ----------
        project_id:
            ID of the project to load.
        """
        ref = self.get_project(project_id)
        declared = (self.workspace_root / ref.path).resolve()
        collection_yaml = _collection_yaml_for_project_path(declared)
        if not collection_yaml.exists():
            raise FileNotFoundError(
                f"collection.yaml not found for project '{project_id}': {collection_yaml}"
            )
        return CollectionConfig.from_yaml(collection_yaml)

    def list_projects(self) -> list[ProjectRef]:
        """Return all declared projects in workspace order."""
        return list(self.projects)


def _collection_yaml_for_project_path(path: Path) -> Path:
    """Return the best collection.yaml candidate for a workspace project path."""
    direct = path / "collection.yaml"
    if direct.exists():
        return direct

    for child in ("interior", "typeset"):
        candidate = path / child / "collection.yaml"
        if candidate.exists():
            return candidate

    if path.name == "typeset":
        migrated = path.parent / "interior" / "collection.yaml"
        if migrated.exists():
            return migrated
    elif path.name == "interior":
        legacy = path.parent / "typeset" / "collection.yaml"
        if legacy.exists():
            return legacy

    return direct
