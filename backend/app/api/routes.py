from __future__ import annotations

from fastapi import APIRouter

from app.schemas.news import DashboardOverview, HeartbeatStatus, NewsAnalysisRequest, NewsAnalysisResponse
from app.services.news_analysis import analysis_service
from app.services.storage import store
from app.tasks.scheduler import scheduler_service

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "econews-backend"}


@router.post("/analyze", response_model=NewsAnalysisResponse)
async def analyze_news(payload: NewsAnalysisRequest) -> NewsAnalysisResponse:
    analysis = analysis_service.analyze(payload)
    store.add_analysis(analysis)
    return analysis


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def dashboard_overview() -> DashboardOverview:
    return store.get_overview()


@router.get("/dashboard/feed")
async def dashboard_feed(limit: int = 20) -> list[dict]:
    return store.get_feed(limit=limit)


@router.get("/dashboard/analyses", response_model=list[NewsAnalysisResponse])
async def dashboard_analyses(limit: int = 10) -> list[NewsAnalysisResponse]:
    return store.get_recent_analyses(limit=limit)


@router.get("/system/heartbeats", response_model=list[HeartbeatStatus])
async def system_heartbeats() -> list[HeartbeatStatus]:
    return store.get_heartbeats()


@router.post("/crawlers/run-once")
async def run_crawlers_once() -> dict:
    return await scheduler_service.run_crawlers_once()

