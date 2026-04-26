from __future__ import annotations

from collections import Counter, deque
from datetime import datetime

from app.schemas.news import DashboardOverview, HeartbeatStatus, NewsAnalysisResponse


class InMemoryStore:
    def __init__(self) -> None:
        self.analyses: deque[NewsAnalysisResponse] = deque(maxlen=200)
        self.feed: deque[dict] = deque(maxlen=100)
        self.heartbeats: dict[str, HeartbeatStatus] = {}

    def add_analysis(self, analysis: NewsAnalysisResponse) -> None:
        self.analyses.appendleft(analysis)

    def add_feed_item(self, item: dict) -> None:
        self.feed.appendleft(item)

    def update_heartbeat(self, heartbeat: HeartbeatStatus) -> None:
        self.heartbeats[heartbeat.source] = heartbeat

    def get_overview(self) -> DashboardOverview:
        analyses = list(self.analyses)
        total_events = len(analyses)
        strong_events = sum(1 for item in analyses if item.impact_score.NIS_total > 0.6)
        avg_nis = round(
            sum(item.impact_score.NIS_total for item in analyses) / total_events,
            4,
        ) if analyses else 0.0
        counter = Counter(item.event_type for item in analyses)
        top_event_type = counter.most_common(1)[0][0] if counter else "暂无数据"
        return DashboardOverview(
            total_events=total_events,
            strong_events=strong_events,
            avg_nis=avg_nis,
            top_event_type=top_event_type,
            latest_updated_at=datetime.utcnow(),
        )

    def get_recent_analyses(self, limit: int = 10) -> list[NewsAnalysisResponse]:
        return list(self.analyses)[:limit]

    def get_feed(self, limit: int = 20) -> list[dict]:
        return list(self.feed)[:limit]

    def get_heartbeats(self) -> list[HeartbeatStatus]:
        return list(self.heartbeats.values())


store = InMemoryStore()

