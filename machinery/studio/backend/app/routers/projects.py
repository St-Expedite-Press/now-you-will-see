from __future__ import annotations

from fastapi import APIRouter

from app.models.project import ProjectCreate, ProjectDetail, WorkspaceInfo
from app.services import project_service

router = APIRouter()


@router.get("", response_model=WorkspaceInfo)
async def list_projects() -> WorkspaceInfo:
    return project_service.get_workspace()


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str) -> ProjectDetail:
    return project_service.get_project(project_id)


@router.post("", response_model=ProjectDetail, status_code=201)
async def create_project(body: ProjectCreate) -> ProjectDetail:
    return project_service.create_project(body)
