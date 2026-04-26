from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.crawlers.eastmoney import EastMoneyCrawler
from app.crawlers.yicai import YicaiCrawler
from app.schemas.news import HeartbeatStatus, NewsAnalysisRequest
from app.services.news_analysis import analysis_service
from app.services.storage import store


class SchedulerService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.crawlers = [EastMoneyCrawler(), YicaiCrawler()]
        self.started = False

    async def start(self) -> None:
        if self.started:
            return
        self.scheduler.add_job(
            self.run_crawlers_once,
            "interval",
            seconds=self.settings.crawler_interval_seconds,
            id="crawler-cycle",
            max_instances=1,
            coalesce=True,
        )
        self.scheduler.start()
        await self.run_crawlers_once()
        self.started = True

    async def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        for crawler in self.crawlers:
            await crawler.close()
        self.started = False

    async def run_crawlers_once(self) -> dict:
        total = 0
        for crawler in self.crawlers:
            status = "ok"
            message = "采集正常"
            try:
                items = await crawler.fetch_latest()
                total += len(items)
                for item in items:
                    store.add_feed_item(
                        {
                            "title": item.title,
                            "source": item.source,
                            "published_at": item.published_at,
                            "url": item.url,
                        }
                    )
                    analysis = analysis_service.analyze(
                        NewsAnalysisRequest(
                            news_title=item.title,
                            news_content=item.content,
                            source=item.source,
                            published_at=item.published_at,
                        )
                    )
                    store.add_analysis(analysis)
            except Exception as exc:
                items = []
                status = "degraded"
                message = f"采集失败，已切换降级样本: {exc}"

            store.update_heartbeat(
                HeartbeatStatus(
                    source=crawler.source_name,
                    status=status,
                    last_run=datetime.utcnow(),
                    latest_count=len(items),
                    message=message,
                )
            )
        return {"status": "ok", "fetched": total}


scheduler_service = SchedulerService()

