from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.services.knowledge_base import EVENT_TEMPLATES
from app.services.nlp_provider import HeuristicNLPProvider, ProviderResult

logger = logging.getLogger(__name__)

# Zero-Shot 分类候选标签集
CLASSIFICATION_LABELS = [t["label"] for t in EVENT_TEMPLATES]


@dataclass
class SentimentOutput:
    label: str
    score: float


class BertNLPProvider:
    """基于预训练模型的 NLP 提供者，使用 Zero-Shot 分类、NER 和情感分析。"""

    def __init__(self, device: str = "auto", fp16: bool = False) -> None:
        self._device = self._resolve_device(device)
        self._fp16 = fp16
        self._zero_shot_pipe = None
        self._ner_pipe = None
        self._sentiment_pipe = None
        self._heuristic_fallback = HeuristicNLPProvider()
        self._initialized = False

    def _resolve_device(self, device: str) -> str:
        if device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return

        try:
            from transformers import pipeline
        except ImportError as e:
            logger.warning("transformers not available, falling back to heuristic: %s", e)
            return

        model_kwargs = {"torch_dtype": "float16"} if self._fp16 else {}

        try:
            self._zero_shot_pipe = pipeline(
                "zero-shot-classification",
                model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
                device=self._device if self._device != "cpu" else -1,
            )
            logger.info("Zero-Shot 分类模型加载完成")
        except Exception as e:
            logger.warning("Zero-Shot 模型加载失败: %s", e)

        try:
            self._ner_pipe = pipeline(
                "ner",
                model="ckiplab/bert-base-chinese-ner",
                aggregation_strategy="simple",
                device=self._device if self._device != "cpu" else -1,
            )
            logger.info("NER 模型加载完成")
        except Exception as e:
            logger.warning("NER 模型加载失败: %s", e)

        try:
            self._sentiment_pipe = pipeline(
                "sentiment-analysis",
                model="hw2942/chinese-finbert",
                device=self._device if self._device != "cpu" else -1,
            )
            logger.info("情感分析模型加载完成")
        except Exception as e:
            logger.warning("情感分析模型加载失败: %s", e)

        self._initialized = True

    def classify(self, title: str, content: str) -> ProviderResult:
        self._ensure_initialized()

        text = f"{title} {content}"
        truncated_text = text[:512]

        template = self._classify_template(truncated_text)
        event_name = self._heuristic_fallback._pick_event_name(text, template)
        subject = self._extract_subject(truncated_text)
        positive_hits, negative_hits, summary_bias = self._analyze_sentiment(truncated_text)

        return ProviderResult(
            template=template,
            event_name=event_name,
            subject=subject,
            positive_hits=positive_hits,
            negative_hits=negative_hits,
            summary_bias=summary_bias,
        )

    def _classify_template(self, text: str) -> dict:
        if self._zero_shot_pipe is None:
            return self._heuristic_fallback.classify(text, "").template

        try:
            result = self._zero_shot_pipe(text, CLASSIFICATION_LABELS, multi_label=True)
            predicted_label = result["labels"][0]
            for template in EVENT_TEMPLATES:
                if template["label"] == predicted_label:
                    return template
        except Exception as e:
            logger.warning("Zero-Shot 分类失败，回退到启发式: %s", e)

        return self._heuristic_fallback.classify(text, "").template

    def _extract_subject(self, text: str) -> str:
        if self._ner_pipe is None:
            return self._heuristic_fallback._extract_subject(text)

        try:
            ner_result = self._ner_pipe(text)
            for entity in ner_result:
                if entity.get("entity_group") == "ORG":
                    return entity["word"]
        except Exception as e:
            logger.warning("NER 提取失败，回退到启发式: %s", e)

        return self._heuristic_fallback._extract_subject(text)

    def _analyze_sentiment(self, text: str) -> tuple[int, int, str]:
        if self._sentiment_pipe is None:
            return (0, 0, "中性偏谨慎")

        try:
            result = self._sentiment_pipe(text[:512])
            if isinstance(result, list) and len(result) > 0:
                sentiment = result[0]
                label = sentiment.get("label", "").lower()
                score = sentiment.get("score", 0.5)

                if label in ["positive", "pos", "正面"]:
                    positive_hits = int(score * 10)
                    negative_hits = 0
                    summary_bias = "偏正向"
                elif label in ["negative", "neg", "负面"]:
                    positive_hits = 0
                    negative_hits = int(score * 10)
                    summary_bias = "偏负向"
                else:
                    positive_hits = 0
                    negative_hits = 0
                    summary_bias = "中性偏谨慎"

                return (positive_hits, negative_hits, summary_bias)
        except Exception as e:
            logger.warning("情感分析失败: %s", e)

        return (0, 0, "中性偏谨慎")

    def score_sentiment(self, positive_hits: int, negative_hits: int) -> float:
        from app.services.scoring import sentiment_intensity
        return sentiment_intensity(positive_hits, negative_hits)