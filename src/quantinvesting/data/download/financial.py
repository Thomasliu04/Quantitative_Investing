from __future__ import annotations

from pathlib import Path

from loguru import logger

from quantinvesting.data.download.base import BaseDownloader
from quantinvesting.data.download.periods import iter_report_periods


class FinancialDownloader(BaseDownloader):
    """L2 financials via VIP APIs: one report period = full market snapshot."""

    name = "financial"

    API_DIRS = {
        "fina_indicator_vip": "fina/fina_indicator",
        "income_vip": "fina/income",
        "balancesheet_vip": "fina/balancesheet",
        "cashflow_vip": "fina/cashflow",
    }

    def run(self, *, dry_run: bool = True, apis: list[str] | None = None) -> None:
        apis = apis or list(self.API_DIRS)
        periods = iter_report_periods(self.start_date(), self.end_date())
        logger.info("financial download {} periods, apis={}", len(periods), apis)

        for api in apis:
            for period in periods:
                if self.already_done(api, period):
                    continue
                out = self._path_for(api, period)
                if dry_run:
                    logger.info("[dry-run] would download {}:{} -> {}", api, period, out)
                    continue
                df = self.call_api(lambda p=period, a=api: self._fetch(a, p), desc=f"{api}:{period}")
                self.save_parquet(df, out)
                self.mark_done(api, period)

    def _path_for(self, api: str, period: str) -> Path:
        return self.raw_root / self.API_DIRS[api] / f"{period}.parquet"

    def _fetch(self, api: str, period: str):
        fn = getattr(self.pro, api)
        return fn(period=period)
