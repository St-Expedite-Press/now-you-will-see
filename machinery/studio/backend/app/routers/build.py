from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.exceptions import BuildError
from app.services import build_service

router = APIRouter()


@router.websocket("/ws")
async def build_ws(project_id: str, websocket: WebSocket, draft: bool = False) -> None:
    """WebSocket endpoint — streams build log lines to the frontend."""
    await websocket.accept()
    try:
        async for line in build_service.stream_build(project_id, draft=draft):
            await websocket.send_text(line)
        await websocket.send_text("[done]\n")
    except BuildError as exc:
        await websocket.send_text(f"[error] {exc}\n")
        await websocket.send_text("[failed]\n")
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.post("/trigger")
async def trigger_build(project_id: str, draft: bool = False) -> dict[str, str]:
    """Fire-and-forget build — returns immediately; use WS for log streaming."""
    import asyncio
    asyncio.create_task(_run(project_id, draft))
    return {"status": "started"}


async def _run(project_id: str, draft: bool) -> None:
    try:
        async for _ in build_service.stream_build(project_id, draft=draft):
            pass
    except BuildError:
        pass
