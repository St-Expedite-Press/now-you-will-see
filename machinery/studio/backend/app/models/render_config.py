"""Pydantic v2 models for per-element render configuration cascade."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ConfigLevel = Literal["global", "section", "poem", "custom"]


class RenderConfigValues(BaseModel):
    """All knobs that can be tuned at any cascade level."""
    mainfont: str | None = None
    fontsize: str | None = None        # e.g. "11pt"
    paperwidth: str | None = None      # e.g. "5.5in"
    paperheight: str | None = None
    top_margin: str | None = None
    bottom_margin: str | None = None
    inner_margin: str | None = None
    outer_margin: str | None = None
    verse_parskip: str | None = None
    stanza_skip: str | None = None
    line_spread: str | None = None


class RenderConfigLayer(BaseModel):
    """One layer in the cascade."""
    level: ConfigLevel
    scope_id: str = ""  # section id or poem slug; empty for global
    values: RenderConfigValues
    source_file: str = ""  # which file this layer was read from


class MergedRenderConfig(BaseModel):
    """Fully resolved config after cascade merge — what the template sees."""
    layers: list[RenderConfigLayer]
    resolved: RenderConfigValues


class RenderConfigUpdate(BaseModel):
    level: ConfigLevel
    scope_id: str = ""
    values: RenderConfigValues
