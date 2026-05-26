"""Workspace management: discover, list, and select projects.

This module provides helpers for locating ``workspace.yaml`` and resolving
a project ID to a :class:`~texgraph.config.CollectionConfig`.

Typical usage::

    from texgraph.workspace import find_workspace, load_workspace, resolve_project

    workspace_path = find_workspace()
    if workspace_path:
        workspace = load_workspace(workspace_path)
        cfg = resolve_project(workspace, project_id="my-project")
    else:
        cfg = CollectionConfig.from_yaml("collection.yaml")
"""

from __future__ import annotations

from pathlib import Path

from texgraph.config import CollectionConfig, WorkspaceConfig

WORKSPACE_FILENAME = "workspace.yaml"


def find_workspace(start: Path | None = None) -> Path | None:
    """Walk up the directory tree from *start* looking for ``workspace.yaml``.

    Parameters
    ----------
    start:
        Directory to begin the search.  Defaults to the current working
        directory when ``None``.

    Returns
    -------
    Path | None
        Absolute path to ``workspace.yaml`` if found, otherwise ``None``.
    """
    current = (start or Path.cwd()).resolve()

    # Walk upward until we hit the filesystem root
    while True:
        candidate = current / WORKSPACE_FILENAME
        if candidate.is_file():
            return candidate

        parent = current.parent
        if parent == current:
            # Reached filesystem root without finding workspace.yaml
            return None
        current = parent


def load_workspace(workspace_path: Path) -> WorkspaceConfig:
    """Load :class:`~texgraph.config.WorkspaceConfig` from *workspace_path*.

    Parameters
    ----------
    workspace_path:
        Path to ``workspace.yaml`` (absolute or relative).

    Returns
    -------
    WorkspaceConfig
        Parsed workspace configuration.
    """
    return WorkspaceConfig.from_yaml(workspace_path)


def resolve_project(
    workspace: WorkspaceConfig,
    project_id: str | None,
) -> CollectionConfig:
    """Return the :class:`~texgraph.config.CollectionConfig` for a project.

    If *project_id* is ``None`` or an empty string, the workspace's
    ``default_project`` is used.

    Parameters
    ----------
    workspace:
        Loaded :class:`~texgraph.config.WorkspaceConfig`.
    project_id:
        ID of the desired project, or ``None`` to use the default.

    Returns
    -------
    CollectionConfig
        Configuration for the resolved project.

    Raises
    ------
    ValueError
        If *project_id* is ``None`` and no ``default_project`` is set.
    KeyError
        If the requested project ID does not exist in the workspace.
    """
    effective_id = project_id or workspace.default_project
    if not effective_id:
        raise ValueError(
            "No project specified and no 'default_project' set in workspace.yaml. "
            "Use --project <id> to select a project."
        )
    return workspace.get_collection_config(effective_id)
