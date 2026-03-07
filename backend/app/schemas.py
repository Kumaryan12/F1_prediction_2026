from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class PredictionRow(BaseModel):
    driver: str
    team: str
    grid_pos: Optional[int] = None

    pred_finish: float
    pred_std: float
    pred_rank: int

    pi68_low: Optional[float] = None
    pi68_high: Optional[float] = None
    pi95_low: Optional[float] = None
    pi95_high: Optional[float] = None

    pred_low: Optional[float] = None
    pred_high: Optional[float] = None

    p_top10: Optional[float] = None
    p_podium: Optional[float] = None
    p_rank_pm1: Optional[float] = None

    driver_2026_session_strength: Optional[float] = None
    team_2026_strength: Optional[float] = None
    driver_strength_blend_2026: Optional[float] = None
    team_strength_blend_2026: Optional[float] = None

    pred_finish_model: Optional[float] = None
    pred_rank_model: Optional[int] = None
    session_boost: Optional[float] = None


class PredictionsResponse(BaseModel):
    race: str
    total_rows: int
    rows: List[PredictionRow]


class DriverResponse(BaseModel):
    row: PredictionRow


class SummaryResponse(BaseModel):
    race: str
    total_drivers: int
    predicted_winner: str
    predicted_podium: List[str]
    best_team: str
    avg_pred_std: float = Field(..., description="Average uncertainty across all drivers")