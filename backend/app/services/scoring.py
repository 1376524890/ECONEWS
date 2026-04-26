from __future__ import annotations


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, round(value, 4)))


def compute_nis(E: float, S: float, R: float, C: float, A: float) -> float:
    return clamp(0.30 * E + 0.25 * S + 0.20 * R + 0.15 * C + 0.10 * A)


def impact_level(score: float) -> str:
    if score <= 0.2:
        return "弱影响"
    if score <= 0.4:
        return "轻度影响"
    if score <= 0.6:
        return "中等影响"
    if score <= 0.8:
        return "较强影响"
    return "强影响"


def sentiment_intensity(positive_hits: int, negative_hits: int) -> float:
    total = positive_hits + negative_hits
    if total == 0:
        return 0.45
    imbalance = abs(positive_hits - negative_hits) / total
    baseline = 0.5 + min(total / 20, 0.3)
    return clamp(baseline + 0.2 * imbalance)

