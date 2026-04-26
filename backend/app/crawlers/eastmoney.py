from __future__ import annotations

from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.crawlers.base import NewsCrawlerBase
from app.schemas.news import CrawledNewsItem


class EastMoneyCrawler(NewsCrawlerBase):
    source_name = "东方财富"
    base_url = get_settings().eastmoney_base_url

    def parse_homepage(self, soup: BeautifulSoup) -> list[CrawledNewsItem]:
        items: list[CrawledNewsItem] = []
        for anchor in soup.select("a[href]")[:8]:
            title = anchor.get_text(strip=True)
            href = anchor.get("href", "")
            if len(title) < 12:
                continue
            items.append(
                self.build_item(
                    title=title,
                    content=f"{title}。该文本为东方财富首页抓取摘要，等待详情页扩展。",
                    url=href,
                )
            )
        return items or self.seed_items()

    def seed_items(self) -> list[CrawledNewsItem]:
        return [
            self.build_item(
                title="央行开展公开市场操作并保持流动性合理充裕",
                content="央行通过公开市场操作稳定短端资金利率，市场关注后续LPR与信贷投放节奏。",
            ),
            self.build_item(
                title="专项债发行节奏加快 基建链投资预期升温",
                content="多地专项债项目加速落地，基建和建材链条需求改善预期升温。",
            ),
        ]

