from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger

from quantinvesting.data.download.base import BaseDownloader


class DailyDownloader(BaseDownloader):
    """L1 market data: pull full cross-section per trade_date (not per stock)."""

    name = "daily"

    API_DIRS = {
        "daily": "daily",
        "daily_basic": "daily_basic",
        "adj_factor": "adj_factor",
    }

    def run(self, *, dry_run: bool = True, apis: list[str] | None = None) -> None:
        apis = apis or list(self.API_DIRS)
        trade_dates = self._list_trade_dates(dry_run=dry_run)
        logger.info("daily download window {} -> {}, {} open days, apis={}", self.start_date(), self.end_date(), len(trade_dates), apis)

        for api in apis:
            for trade_date in trade_dates:
                if self.already_done(api, trade_date):
                    continue
                out = self._path_for(api, trade_date)
                if dry_run:
                    logger.info("[dry-run] would download {}:{} -> {}", api, trade_date, out)
                    continue
                df = self.call_api(lambda d=trade_date, a=api: self._fetch(a, d), desc=f"{api}:{trade_date}")
                self.save_parquet(df, out)
                self.mark_done(api, trade_date)

    def _path_for(self, api: str, trade_date: str) -> Path:
        year = trade_date[:4]
        return self.raw_root / self.API_DIRS[api] / year / f"{trade_date}.parquet"

    def _list_trade_dates(self, *, dry_run: bool) -> list[str]:
        cal_path = self.raw_root / "meta" / "trade_cal.parquet"
        if cal_path.exists():
            cal = pd.read_parquet(cal_path)
            open_days = cal.loc[cal["is_open"] == 1, "cal_date"].astype(str)
            mask = (open_days >= self.start_date()) & (open_days <= self.end_date())
            return open_days.loc[mask].tolist()

        # Fallback skeleton list so dry-run works before meta download.
        if dry_run:
            logger.warning("trade_cal missing; dry-run uses placeholder dates")
            return [self.start_date(), self.end_date()]
        raise FileNotFoundError(f"Missing {cal_path}; run meta download first.")

    def _fetch(self, api: str, trade_date: str) -> pd.DataFrame:
        if api == "daily":
            return self.pro.daily(trade_date=trade_date)
        if api == "daily_basic":
            return self.pro.daily_basic(trade_date=trade_date)
        if api == "adj_factor":
            return self.pro.adj_factor(trade_date=trade_date)
        raise ValueError(f"unsupported daily api: {api}")
