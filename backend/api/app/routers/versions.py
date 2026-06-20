from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from app.models.version import VersionCreate, VersionList, VersionSetCanonical, VersionUpdate
from app.services import poem_service, version_service

router = APIRouter()


def _sec_dir(project_id: str, section_id: str) -> Path:
    return poem_service._section_dir(project_id, section_id)


@router.get("", response_model=VersionList)
async def list_versions(project_id: str, section_id: str, poem_slug: str) -> VersionList:
    return version_service.list_versions(_sec_dir(project_id, section_id), poem_slug)


@router.post("", response_model=VersionList, status_code=201)
async def create_version(project_id: str, section_id: str, poem_slug: str, body: VersionCreate) -> VersionList:
    return version_service.create_version(_sec_dir(project_id, section_id), poem_slug, body)


@router.post("/canonical", response_model=VersionList)
async def set_canonical(project_id: str, section_id: str, poem_slug: str, body: VersionSetCanonical) -> VersionList:
    return version_service.set_canonical(_sec_dir(project_id, section_id), poem_slug, body)
