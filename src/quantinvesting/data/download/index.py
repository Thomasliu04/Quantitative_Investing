from __future__ import annotations

from loguru import logger

from quantinvesting.data.download.base import BaseDownloader


class IndexDownloader(BaseDownloader):
    """L3 index prices and constituent weights (skeleton)."""

    name = "index"

    DEFAULT_INDEXES = (
        "000905.SH",  # CSI 500
        "000852.SH",  # CSI 1000
        "000906.SH",  # CSI 800
        "000300.SH",  # CSI 300
    )

    def run(self, *, dry_run: bool = True, indexes: tuple[str, ...] | None = None) -> None:
        indexes = indexes or self.DEFAULT_INDEXES
        for index_code in indexes:
            for api in ("index_daily", "index_weight"):
                key = index_code
                if self.already_done(api, key):
                    continue
                out = self.raw_root / "index" / api / f"{index_code.replace('.', '_')}.parquet"
                if dry_run:
                    logger.info("[dry-run] would download {}:{} -> {}", api, key, out)
                    continue
                df = self.call_api(lambda a=api, c=index_code: self._fetch(a, c), desc=f"{api}:{key}")
                self.save_parquet(df, out)
                self.mark_done(api, key)

    def _fetch(self, api: str, index_code: str):
        if api == "index_daily":
            return self.pro.index_daily(
                ts_code=index_code,
                start_date=self.start_date(),
                end_date=self.end_date(),
            )
        if api == "index_weight":
            return self.pro.index_weight(
                index_code=index_code,
                start_date=self.start_date(),
                end_date=self.end_date(),
            )
        raise ValueError(api)
