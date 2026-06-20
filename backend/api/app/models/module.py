"""Pydantic models for semantic project modules."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectModule(BaseModel):
    id: str
    label: str
    description: str = ""
    path: str
    exists: bool
    legacy_stage: str | None = None
    legacy_path: str | None = None
    workspace_alias: bool = False
    verify_stage: str | None = None


class ProjectModuleList(BaseModel):
    project_id: str
    modules: list[ProjectModule]


class ModuleVerifyResult(BaseModel):
    project_id: str
    module_id: str
    ok: bool
    status: str
    verify_stage: str | None = None
    checked_path: str
    issues: list[str] = Field(default_factory=list)
