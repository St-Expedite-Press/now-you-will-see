from __future__ import annotations

from pydantic import BaseModel


class CoverAsset(BaseModel):
    filename: str
    rel_path: str
    author: str
    book: str
    role: str
    variant: str
    url: str


class TypographyRegime(BaseModel):
    id: str
    name: str
    face: str
    alignment: str
    distinctive: str
    active: bool = False


class CoverAssetsResponse(BaseModel):
    assets: list[CoverAsset]
    total: int


class CoverRegimesResponse(BaseModel):
    regimes: list[TypographyRegime]
    active_regime: str | None
