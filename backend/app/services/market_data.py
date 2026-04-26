from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from app.core.config import get_settings
from app.schemas.news import EventStudy


FALLBACK_MESSAGE = "当前缺少市场数据，暂无法进行事件研究法验证"


class MarketDataService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def study_event(
        self,
        related_assets: list[str],
        benchmark: str,
        event_date: datetime | None,
    ) -> EventStudy:
        if not related_assets:
            return self._fallback()

        start = (event_date or datetime.utcnow()) - timedelta(days=2)
        end = (event_date or datetime.utcnow()) + timedelta(days=10)

        try:
            asset_symbol = related_assets[0]
            asset_df = self._fetch_asset_frame(asset_symbol, start, end)
            bench_df = self._fetch_asset_frame(benchmark, start, end, is_index=True)
            merged = self._prepare_returns(asset_df, bench_df)
            if merged.empty:
                return self._fallback()

            cutoff = pd.to_datetime((event_date or datetime.utcnow()).date())
            event_window = merged.loc[merged["trade_date"] >= cutoff].head(6).copy()
            if event_window.empty:
                return self._fallback()

            event_window["AR"] = event_window["asset_return"] - event_window["benchmark_return"]
            car = event_window["AR"].sum()
            ar_text = ", ".join(
                f"{idx.strftime('%Y-%m-%d')}:{value:.4%}"
                for idx, value in zip(event_window["trade_date"], event_window["AR"])
            )
            verification = (
                "事件窗口内CAR为正，市场反应与偏正向分析较一致。"
                if car > 0
                else "事件窗口内CAR为负，市场反应偏弱，需警惕逻辑兑现不足。"
            )
            return EventStudy(
                window="T日至T+5",
                AR=ar_text,
                CAR=f"{car:.4%}",
                verification_result=verification,
            )
        except Exception:
            return self._fallback()

    def _prepare_returns(self, asset_df: pd.DataFrame, bench_df: pd.DataFrame) -> pd.DataFrame:
        asset = asset_df[["trade_date", "close"]].copy()
        bench = bench_df[["trade_date", "close"]].copy()
        asset["trade_date"] = pd.to_datetime(asset["trade_date"])
        bench["trade_date"] = pd.to_datetime(bench["trade_date"])
        asset = asset.sort_values("trade_date")
        bench = bench.sort_values("trade_date")
        asset["asset_return"] = asset["close"].pct_change()
        bench["benchmark_return"] = bench["close"].pct_change()
        merged = asset.merge(bench, on="trade_date", how="inner").dropna()
        return merged[["trade_date", "asset_return", "benchmark_return"]]

    def _fetch_asset_frame(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        is_index: bool = False,
    ) -> pd.DataFrame:
        normalized = symbol.split(".")[0]
        if is_index:
            try:
                import akshare as ak

                df = ak.index_zh_a_hist(
                    symbol=normalized,
                    period="daily",
                    start_date=start.strftime("%Y%m%d"),
                    end_date=end.strftime("%Y%m%d"),
                )
                return df.rename(columns={"日期": "trade_date", "收盘": "close"})
            except Exception:
                pass

        try:
            import akshare as ak

            df = ak.stock_zh_a_hist(
                symbol=normalized,
                period="daily",
                start_date=start.strftime("%Y%m%d"),
                end_date=end.strftime("%Y%m%d"),
                adjust="qfq",
            )
            return df.rename(columns={"日期": "trade_date", "收盘": "close"})
        except Exception:
            pass

        if self.settings.tushare_token:
            try:
                import tushare as ts

                ts.set_token(self.settings.tushare_token)
                pro = ts.pro_api()
                df = pro.daily(
                    ts_code=symbol,
                    start_date=start.strftime("%Y%m%d"),
                    end_date=end.strftime("%Y%m%d"),
                )
                return df.rename(columns={"trade_date": "trade_date", "close": "close"})
            except Exception:
                pass

        raise RuntimeError("Market data unavailable")

    def _fallback(self) -> EventStudy:
        return EventStudy(
            window="T日至T+5",
            AR="",
            CAR="",
            verification_result=FALLBACK_MESSAGE,
        )

