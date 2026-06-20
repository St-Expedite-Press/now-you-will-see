from __future__ import annotations

from fastapi import APIRouter

from app.models.module import ModuleVerifyResult, ProjectModule, ProjectModuleList
from app.services import module_service

router = APIRouter()


@router.get("", response_model=ProjectModuleList)
async def list_project_modules(project_id: str) -> ProjectModuleList:
    return module_service.list_modules(project_id)


@router.get("/{module_id}", response_model=ProjectModule)
async def get_project_module(project_id: str, module_id: str) -> ProjectModule:
    return module_service.get_module(project_id, module_id)


@router.post("/{module_id}/verify", response_model=ModuleVerifyResult)
async def verify_project_module(project_id: str, module_id: str) -> ModuleVerifyResult:
    return module_service.verify_module(project_id, module_id)
