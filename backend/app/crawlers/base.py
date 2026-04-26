from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from app.schemas.news import CrawledNewsItem


class NewsCrawlerBase(ABC):
    source_name: str = ""
    base_url: str = ""

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self.client = httpx.AsyncClient(
            timeout=10.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": self.base_url,
            },
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def fetch_latest(self) -> list[CrawledNewsItem]:
        try:
            response = await self.client.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            items = self.parse_homepage(soup)
        except Exception:
            items = self.seed_items()

        fresh_items = []
        for item in items:
            fingerprint = self._fingerprint(item)
            if fingerprint in self._seen:
                continue
            self._seen.add(fingerprint)
            fresh_items.append(item)
        return fresh_items

    def _fingerprint(self, item: CrawledNewsItem) -> str:
        payload = f"{item.source}|{item.title}|{item.published_at}|{item.url}"
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

    @abstractmethod
    def parse_homepage(self, soup: BeautifulSoup) -> list[CrawledNewsItem]:
        raise NotImplementedError

    @abstractmethod
    def seed_items(self) -> list[CrawledNewsItem]:
        raise NotImplementedError

    def build_item(
        self,
        title: str,
        content: str,
        url: str = "",
        published_at: datetime | None = None,
    ) -> CrawledNewsItem:
        return CrawledNewsItem(
            title=title,
            content=content,
            source=self.source_name,
            url=url,
            published_at=published_at or datetime.utcnow(),
        )

