from __future__ import annotations

from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.crawlers.base import NewsCrawlerBase
from app.schemas.news import CrawledNewsItem


class YicaiCrawler(NewsCrawlerBase):
    source_name = "第一财经"
    base_url = get_settings().yicai_base_url

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
                    content=f"{title}。该文本为第一财经首页抓取摘要，等待详情页扩展。",
                    url=href,
                )
            )
        return items or self.seed_items()

    def seed_items(self) -> list[CrawledNewsItem]:
        return [
            self.build_item(
                title="统计局公布制造业PMI数据 市场关注景气度变化",
                content="制造业PMI数据将影响市场对需求恢复、企业盈利和政策力度的判断。",
            ),
            self.build_item(
                title="美联储释放偏鹰信号 全球资产重新定价",
                content="海外利率预期上修压制全球风险偏好，汇率和成长资产面临再平衡。",
            ),
        ]

