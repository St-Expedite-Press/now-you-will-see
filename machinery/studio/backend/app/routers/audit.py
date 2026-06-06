from __future__ import annotations

from fastapi import APIRouter

from app.models.audit import AuditRun
from app.services import audit_service

router = APIRouter()


@router.post("/run", response_model=AuditRun)
async def run_audit() -> AuditRun:
    return audit_service.run_audit()
