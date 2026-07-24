from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from quantinvesting.utils.config import resolve_path


class CleanPipeline:
    """Skeleton for raw -> clean transforms.

    Planned steps (not executed yet):
    1. Adjust prices with adj_factor (VWAP for labels)
    2. Align to trade calendar; mark suspend / zero-volume
    3. Map financials by ann_date / f_ann_date (no look-ahead)
    4. Universe filters: ST / young listings
    5. Factor preprocess: MAD -> zscore -> neutralize -> fillna
    """

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.raw_root = resolve_path(cfg["paths"]["raw"])
        self.clean_root = resolve_path(cfg["paths"]["clean"])
        self.clean_cfg = cfg.get("clean", {})

    def run(self, *, dry_run: bool = True) -> None:
        steps = [
            "build_adjusted_bars",
            "align_financials_pit",
            "build_universe_mask",
            "build_factor_panel",
            "preprocess_factors",
            "build_labels",
        ]
        for step in steps:
            out = self.clean_root / f"{step}.parquet"
            if dry_run:
                logger.info("[dry-run] clean step '{}' -> {}", step, out)
                continue
            logger.warning("clean step '{}' not implemented yet", step)

    def planned_outputs(self) -> list[Path]:
        return [
            self.clean_root / "bars_adj.parquet",
            self.clean_root / "fina_pit.parquet",
            self.clean_root / "universe.parquet",
            self.clean_root / "factors.parquet",
            self.clean_root / "labels.parquet",
        ]
