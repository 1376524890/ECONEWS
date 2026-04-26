from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class VariableImpact(BaseModel):
    variable: str
    direction: str
    logic: str
    meaning: str


class AffectedTarget(BaseModel):
    name: str
    category: str
    direction: Literal["利多", "利空", "中性", "不确定"]
    rationale: str


class ImpactScore(BaseModel):
    E: float = Field(..., ge=0, le=1)
    S: float = Field(..., ge=0, le=1)
    R: float = Field(..., ge=0, le=1)
    C: float = Field(..., ge=0, le=1)
    A: float = Field(..., ge=0, le=1)
    NIS_total: float = Field(..., ge=0, le=1)
    impact_level: str


class EventStudy(BaseModel):
    window: str
    AR: str
    CAR: str
    verification_result: str


class NewsAnalysisResponse(BaseModel):
    news_title: str
    event_type: str
    event_name: str
    event_subject: str
    summary: str
    economic_variables: list[VariableImpact]
    transmission_chain: str
    affected_targets: list[AffectedTarget]
    impact_score: ImpactScore
    event_study: EventStudy
    decision_support: str
    risk_warning: str


class NewsAnalysisRequest(BaseModel):
    news_title: str = Field(..., min_length=4)
    news_content: str = Field(..., min_length=20)
    source: str = "manual"
    published_at: datetime | None = None
    related_assets: list[str] = Field(default_factory=list)
    benchmark: str = "000300.SH"


class CrawledNewsItem(BaseModel):
    title: str
    content: str
    source: str
    url: str = ""
    published_at: datetime | None = None


class DashboardOverview(BaseModel):
    total_events: int
    strong_events: int
    avg_nis: float
    top_event_type: str
    latest_updated_at: datetime


class HeartbeatStatus(BaseModel):
    source: str
    status: str
    last_run: datetime | None = None
    latest_count: int = 0
    message: str = ""

