from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from quantinvesting.utils.config import resolve_path


class QualityChecker:
    """Lightweight data QA after download / clean."""

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.raw_root = resolve_path(cfg["paths"]["raw"])
        self.meta_root = resolve_path(cfg["paths"]["meta"])

    def run(self) -> dict[str, Any]:
        report: dict[str, Any] = {}
        cal_path = self.raw_root / "meta" / "trade_cal.parquet"
        if cal_path.exists():
            cal = pd.read_parquet(cal_path)
            open_days = cal.loc[cal["is_open"] == 1, "cal_date"].astype(str)
            report["n_open_days"] = int(open_days.shape[0])
            report["missing_daily_files"] = self._missing_by_date("daily", open_days.tolist())
        else:
            report["trade_cal"] = "missing"

        report["raw_file_counts"] = {
            "daily": self._count_parquets(self.raw_root / "daily"),
            "daily_basic": self._count_parquets(self.raw_root / "daily_basic"),
            "adj_factor": self._count_parquets(self.raw_root / "adj_factor"),
            "fina": self._count_parquets(self.raw_root / "fina"),
        }
        logger.info("QA report: {}", report)
        return report

    def _count_parquets(self, root: Path) -> int:
        if not root.exists():
            return 0
        return sum(1 for _ in root.rglob("*.parquet"))

    def _missing_by_date(self, api: str, trade_dates: list[str]) -> list[str]:
        missing = []
        for d in trade_dates:
            path = self.raw_root / api / d[:4] / f"{d}.parquet"
            if not path.exists():
                missing.append(d)
        # Only return head to keep report small in early stage
        return missing[:20] + (["..."] if len(missing) > 20 else [])
