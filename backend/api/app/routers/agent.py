from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.core.exceptions import AgentError
from app.models.agent import AgentChatRequest, StageChatRequest, StageChatResponse
from app.services import agent_service, runtime_service

router = APIRouter()


# --- Gated per-stage agents (the station runtime) ------------------------------


@router.get("/stages")
def stages() -> dict:
    """The station screens and their stages (framework/pipeline.yaml)."""
    return runtime_service.list_stages()


@router.get("/stage/{stage}")
def describe_stage(stage: str, project_id: str | None = None) -> dict:
    """The gated agent's public shape for a stage: tools, skills, gate, io, scope."""
    return runtime_service.describe_agent(stage, project_id)


@router.post("/stage", response_model=StageChatResponse)
def stage_chat(request: StageChatRequest) -> StageChatResponse:
    """Run one turn for a screen's gated specialist agent (real tool-calling)."""
    result = runtime_service.run_stage_turn(
        request.stage,
        request.project_id,
        [m.model_dump() for m in request.messages],
    )
    return StageChatResponse(**result)


@router.websocket("/ws")
async def agent_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint — receives AgentChatRequest JSON, streams token chunks."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        request = AgentChatRequest.model_validate(data)
        async for token in agent_service.stream_chat(request):
            await websocket.send_text(token)
        await websocket.send_text("\x00")  # null-byte signals end of stream
    except AgentError as exc:
        await websocket.send_text(f"\x01{exc}")  # SOH prefix = error
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.post("/chat")
async def agent_chat_http(request: AgentChatRequest) -> StreamingResponse:
    """HTTP SSE fallback for environments where WebSocket is unavailable."""
    async def _gen():  # type: ignore[return]
        try:
            async for token in agent_service.stream_chat(request):
                yield f"data: {token}\n\n"
        except AgentError as exc:
            yield f"event: error\ndata: {exc}\n\n"
        yield "event: done\ndata: \n\n"

    return StreamingResponse(_gen(), media_type="text/event-stream")
