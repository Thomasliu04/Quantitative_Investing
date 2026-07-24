from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from quantinvesting.utils.config import resolve_path
from quantinvesting.utils.download_log import DownloadLog
from quantinvesting.utils.rate_limit import RateLimiter, with_retry
from quantinvesting.utils.tushare_client import get_tushare_token


class BaseDownloader(ABC):
    """Common helpers: paths, rate limit, retry, resume log, parquet IO."""

    name: str = "base"

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.dl_cfg = cfg.get("download", {})
        self.raw_root = resolve_path(cfg["paths"]["raw"])
        self.meta_root = resolve_path(cfg["paths"]["meta"])
        self.limiter = RateLimiter(float(self.dl_cfg.get("sleep_seconds", 0.15)))
        self.max_retries = int(self.dl_cfg.get("max_retries", 3))
        self.backoff = float(self.dl_cfg.get("retry_backoff_seconds", 2.0))
        self.log = DownloadLog(self.meta_root / "download_log.json")
        self._pro = None

    @property
    def pro(self):
        if self._pro is None:
            import tushare as ts

            self._pro = ts.pro_api(get_tushare_token())
        return self._pro

    def start_date(self) -> str:
        return str(self.dl_cfg.get("start_date", "20180101"))

    def end_date(self) -> str:
        end = self.dl_cfg.get("end_date")
        if end:
            return str(end)
        return datetime.now().strftime("%Y%m%d")

    def log_key(self, api: str, key: str) -> str:
        return f"{api}:{key}"

    def already_done(self, api: str, key: str) -> bool:
        return self.log.has(self.log_key(api, key))

    def mark_done(self, api: str, key: str) -> None:
        self.log.mark(self.log_key(api, key))

    def call_api(self, fn, *, desc: str):
        self.limiter.wait()
        return with_retry(
            fn,
            max_retries=self.max_retries,
            backoff_seconds=self.backoff,
            desc=desc,
        )

    def save_parquet(self, df: pd.DataFrame, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if df is None or df.empty:
            logger.warning("empty frame, skip write: {}", path)
            return
        df.to_parquet(path, index=False)
        logger.info("wrote {} rows -> {}", len(df), path)

    @abstractmethod
    def run(self, *, dry_run: bool = True) -> None:
        raise NotImplementedError
