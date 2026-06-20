from __future__ import annotations

from fastapi import APIRouter

from app.models.render_config import MergedRenderConfig, RenderConfigLayer, RenderConfigUpdate
from app.services import render_config_service

router = APIRouter()


@router.get("/global", response_model=RenderConfigLayer)
async def get_global(project_id: str) -> RenderConfigLayer:
    return render_config_service.get_global(project_id)


@router.get("/section/{section_id}", response_model=RenderConfigLayer)
async def get_section_config(project_id: str, section_id: str) -> RenderConfigLayer:
    return render_config_service.get_section(project_id, section_id)


@router.get("/merged", response_model=MergedRenderConfig)
async def get_merged(
    project_id: str,
    section_id: str | None = None,
    poem_slug: str | None = None,
) -> MergedRenderConfig:
    return render_config_service.get_merged(project_id, section_id, poem_slug)


@router.put("", response_model=MergedRenderConfig)
async def update_config(project_id: str, body: RenderConfigUpdate) -> MergedRenderConfig:
    return render_config_service.update_config(project_id, body)
