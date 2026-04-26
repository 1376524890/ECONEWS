from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.knowledge_base import (
    EVENT_TEMPLATES,
    NEGATIVE_TERMS,
    POSITIVE_TERMS,
    SUBJECT_PATTERNS,
)
from app.services.scoring import sentiment_intensity


@dataclass
class ProviderResult:
    template: dict
    event_name: str
    subject: str
    positive_hits: int
    negative_hits: int
    summary_bias: str


class HeuristicNLPProvider:
    """Rule-based fallback implementation behind the future model interface."""

    def classify(self, title: str, content: str) -> ProviderResult:
        text = f"{title} {content}"
        scored_templates = []
        for template in EVENT_TEMPLATES:
            hits = sum(text.count(keyword) for keyword in template["keywords"])
            scored_templates.append((hits, template["importance"], template))

        scored_templates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        template = scored_templates[0][2]

        event_name = self._pick_event_name(text, template)
        subject = self._extract_subject(text)
        positive_hits = sum(text.count(token) for token in POSITIVE_TERMS)
        negative_hits = sum(text.count(token) for token in NEGATIVE_TERMS)
        summary_bias = self._resolve_bias(positive_hits, negative_hits)

        return ProviderResult(
            template=template,
            event_name=event_name,
            subject=subject,
            positive_hits=positive_hits,
            negative_hits=negative_hits,
            summary_bias=summary_bias,
        )

    def score_sentiment(self, positive_hits: int, negative_hits: int) -> float:
        return sentiment_intensity(positive_hits, negative_hits)

    def _pick_event_name(self, text: str, template: dict) -> str:
        for keyword in template["keywords"]:
            if keyword in text:
                return f"{template['label']}-{keyword}"
        return template["label"]

    def _extract_subject(self, text: str) -> str:
        for pattern in SUBJECT_PATTERNS:
            if pattern in text:
                return pattern

        regex = re.compile(r"([^\s，。、；：]{2,20}(?:部|委|局|行|会|司|集团|公司|银行))")
        match = regex.search(text)
        if match:
            return match.group(1)

        return "市场主体未明确，需人工复核"

    def _resolve_bias(self, positive_hits: int, negative_hits: int) -> str:
        if positive_hits == negative_hits:
            return "中性偏谨慎"
        if positive_hits > negative_hits:
            return "偏正向"
        return "偏负向"

