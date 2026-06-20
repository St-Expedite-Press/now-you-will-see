from __future__ import annotations

from fastapi import APIRouter

from app.models.poem import PoemCreate, PoemDetail, PoemRaw, PoemSummary, PoemUpdate
from app.services import poem_service

router = APIRouter()


@router.get("", response_model=list[PoemSummary])
async def list_poems(project_id: str, section_id: str) -> list[PoemSummary]:
    return poem_service.list_poems(project_id, section_id)


@router.get("/{poem_slug}", response_model=PoemDetail)
async def get_poem(project_id: str, section_id: str, poem_slug: str) -> PoemDetail:
    return poem_service.get_poem(project_id, section_id, poem_slug)


@router.get("/{poem_slug}/raw", response_model=PoemRaw)
async def get_poem_raw(project_id: str, section_id: str, poem_slug: str) -> PoemRaw:
    return poem_service.get_poem_raw(project_id, section_id, poem_slug)


@router.post("", response_model=PoemDetail, status_code=201)
async def create_poem(project_id: str, section_id: str, body: PoemCreate) -> PoemDetail:
    return poem_service.create_poem(project_id, section_id, body)


@router.put("/{poem_slug}", response_model=PoemDetail)
async def update_poem(project_id: str, section_id: str, poem_slug: str, body: PoemUpdate) -> PoemDetail:
    return poem_service.update_poem(project_id, section_id, poem_slug, body)


@router.delete("/{poem_slug}", status_code=204)
async def delete_poem(project_id: str, section_id: str, poem_slug: str) -> None:
    poem_service.delete_poem(project_id, section_id, poem_slug)
