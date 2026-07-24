from __future__ import annotations

from loguru import logger

from quantinvesting.data.download.base import BaseDownloader


class MetaDownloader(BaseDownloader):
    """L0 metadata: stock list, trade calendar, industry classification."""

    name = "meta"

    def run(self, *, dry_run: bool = True) -> None:
        tasks = [
            ("stock_basic", self._fetch_stock_basic, self.raw_root / "meta" / "stock_basic.parquet"),
            ("trade_cal", self._fetch_trade_cal, self.raw_root / "meta" / "trade_cal.parquet"),
            ("index_classify", self._fetch_index_classify, self.raw_root / "meta" / "index_classify.parquet"),
        ]
        for api, fetcher, path in tasks:
            key = "full"
            if self.already_done(api, key):
                logger.info("[skip] {}:{}", api, key)
                continue
            if dry_run:
                logger.info("[dry-run] would download {} -> {}", api, path)
                continue
            df = self.call_api(fetcher, desc=api)
            self.save_parquet(df, path)
            self.mark_done(api, key)

    def _fetch_stock_basic(self):
        return self.pro.stock_basic(
            exchange="",
            list_status="L",
            fields="ts_code,symbol,name,area,industry,market,list_date,delist_date,list_status",
        )

    def _fetch_trade_cal(self):
        return self.pro.trade_cal(
            exchange="SSE",
            start_date=self.start_date(),
            end_date=self.end_date(),
            fields="exchange,cal_date,is_open,pretrade_date",
        )

    def _fetch_index_classify(self):
        # Shenwan industry classification (L1/L2 as available)
        return self.pro.index_classify(level="L1", src="SW2021")
