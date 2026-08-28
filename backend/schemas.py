from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    generated_at: datetime
    model_loaded: bool
    cache_ttl_seconds: int


class PredictResponse(BaseModel):
    severe_risk: int = Field(ge=0, le=1)
    probability: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    risk_label: str


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    risk: float = Field(ge=0, le=1)


class HeatmapResponse(BaseModel):
    generated_at: datetime
    total_points: int = Field(ge=0)
    points: list[HeatmapPoint]
    source_points_evaluated: int = Field(ge=0)
    threshold: float = Field(ge=0, le=1)
    used_cache: bool = False
    error: Optional[str] = None

