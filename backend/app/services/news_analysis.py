from __future__ import annotations

import logging
import os
from datetime import datetime

from app.schemas.news import (
    AffectedTarget,
    ImpactScore,
    NewsAnalysisRequest,
    NewsAnalysisResponse,
    VariableImpact,
)
from app.services.knowledge_base import DEFAULT_SUMMARY_TEMPLATE, SOURCE_AUTHORITY
from app.services.market_data import MarketDataService
from app.services.nlp_provider import HeuristicNLPProvider, ProviderResult
from app.services.scoring import clamp, compute_nis, impact_level

logger = logging.getLogger(__name__)


def _create_provider() -> HeuristicNLPProvider:
    provider_type = os.getenv("MODEL_PROVIDER", "heuristic").lower()

    if provider_type == "bert":
        try:
            from app.services.bert_provider import BertNLPProvider

            logger.info("使用 BertNLPProvider 作为 NLP 提供者")
            return BertNLPProvider()
        except ImportError as e:
            logger.warning("transformers 库不可用，回退到启发式提供者: %s", e)
        except Exception as e:
            logger.warning("BertNLPProvider 初始化失败，回退到启发式提供者: %s", e)

    logger.info("使用 HeuristicNLPProvider 作为 NLP 提供者")
    return HeuristicNLPProvider()


class NewsAnalysisService:
    def __init__(self) -> None:
        self.provider = _create_provider()
        self.market_data = MarketDataService()

    def analyze(self, payload: NewsAnalysisRequest) -> NewsAnalysisResponse:
        provider_result = self.provider.classify(payload.news_title, payload.news_content)
        template = provider_result.template
        sentiment_score = self.provider.score_sentiment(
            provider_result.positive_hits,
            provider_result.negative_hits,
        )

        impact_score = self._build_impact_score(
            sentiment_score=sentiment_score,
            authority=SOURCE_AUTHORITY.get(payload.source, SOURCE_AUTHORITY["unknown"]),
            importance=template["importance"],
            coverage=template["coverage"],
            asset_relevance=template["asset_relevance"],
            text=payload.news_title + payload.news_content,
        )

        variables = [VariableImpact(**item) for item in template["variables"]]
        targets = [AffectedTarget(name=name, category=category, direction=direction, rationale=rationale)
                   for name, category, direction, rationale in template["targets"]]

        target_names = "、".join(target.name for target in targets[:3])
        variable_names = "、".join(variable.variable for variable in variables[:3])
        summary = DEFAULT_SUMMARY_TEMPLATE.format(
            event_type=template["event_type"],
            subject=provider_result.subject,
            variables=variable_names,
            targets=target_names,
        )
        summary = f"{summary} 当前新闻语气整体{provider_result.summary_bias}。"

        event_study = self.market_data.study_event(
            related_assets=payload.related_assets,
            benchmark=payload.benchmark,
            event_date=payload.published_at or datetime.utcnow(),
        )

        decision_support = (
            f"建议围绕{variable_names}持续跟踪高频数据、政策落地节奏及受影响资产的成交与估值变化，"
            f"重点验证{template['event_type']}是否形成持续预期差修复。"
        )
        risk_warning = (
            "需警惕新闻摘要与原始政策文本之间存在口径偏差，以及市场已提前定价导致的边际反应减弱。"
            "若后续缺少量化行情或事件窗口内出现更强外生冲击，当前判断需要及时修正。"
        )

        return NewsAnalysisResponse(
            news_title=payload.news_title,
            event_type=template["event_type"],
            event_name=provider_result.event_name,
            event_subject=provider_result.subject,
            summary=summary,
            economic_variables=variables,
            transmission_chain=template["chain"],
            affected_targets=targets,
            impact_score=impact_score,
            event_study=event_study,
            decision_support=decision_support,
            risk_warning=risk_warning,
        )

    def _build_impact_score(
        self,
        sentiment_score: float,
        authority: float,
        importance: float,
        coverage: float,
        asset_relevance: float,
        text: str,
    ) -> ImpactScore:
        emphasis_bonus = 0.04 if any(token in text for token in ["重磅", "超预期", "紧急", "全面"]) else 0.0
        E = clamp(importance + emphasis_bonus)
        S = clamp(sentiment_score)
        R = clamp(authority)
        C = clamp(coverage)
        A = clamp(asset_relevance)
        total = compute_nis(E, S, R, C, A)
        return ImpactScore(
            E=E,
            S=S,
            R=R,
            C=C,
            A=A,
            NIS_total=total,
            impact_level=impact_level(total),
        )


analysis_service = NewsAnalysisService()

