from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EconoNews Intelligence Hub"
    api_v1_prefix: str = "/api/v1"
    scheduler_enabled: bool = True
    crawler_interval_seconds: int = 300
    default_benchmark: str = "000300.SH"
    model_provider: str = "heuristic"
    bert_model_name: str = "Chinese-FinBERT"
    llm_endpoint: str | None = None
    tushare_token: str | None = None
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    eastmoney_base_url: str = "https://finance.eastmoney.com"
    yicai_base_url: str = "https://www.yicai.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

