"""Pydantic v2 models for the Agent Chat / Wizard integration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

MessageRole = Literal["user", "assistant", "system"]
AgentMode = Literal["chat", "wizard"]


class AgentMessage(BaseModel):
    role: MessageRole
    content: str


class ActionChip(BaseModel):
    label: str
    action: str   # identifier for the frontend to handle
    payload: dict[str, object] = {}


class AgentResponse(BaseModel):
    message: str
    action_chips: list[ActionChip] = []
    structured_data: dict[str, object] | None = None


class AgentContext(BaseModel):
    """Context injected into every agent request."""
    project_id: str | None = None
    section_id: str | None = None
    poem_slug: str | None = None
    mode: AgentMode = "chat"
    # Raw file contents injected by agent_service
    collection_yaml: str = ""
    active_section_meta: str = ""
    active_poem_content: str = ""
    notes_md: str = ""
    recent_build_log: str = ""


class AgentChatRequest(BaseModel):
    messages: list[AgentMessage]
    context: AgentContext


class AgentWizardState(BaseModel):
    """Live state of a wizard session — sent to the frontend to show progress."""
    step: int = 1
    total_steps: int = 5
    confirmed_fields: dict[str, object] = {}
    pending_sections: list[str] = []
    is_complete: bool = False
