from app.schemas.news import NewsAnalysisRequest
from app.services.news_analysis import analysis_service


def test_analysis_outputs_required_json_shape():
    result = analysis_service.analyze(
        NewsAnalysisRequest(
            news_title="央行开展公开市场操作 释放流动性呵护信号",
            news_content="央行通过逆回购操作保持银行体系流动性合理充裕，市场预计短端利率压力缓和。",
            source="东方财富",
        )
    )

    assert result.event_type == "货币政策事件"
    assert result.impact_score.NIS_total > 0
    assert result.event_study.verification_result
    assert result.economic_variables
    assert result.affected_targets
