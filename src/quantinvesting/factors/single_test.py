from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class FactorSpec:
    """One fundamental (or other) factor candidate.

    Write economic meaning + expected direction before coding the series.
    """

    name: str
    category: str  # valuation | growth | quality | cashflow | ...
    direction: int  # +1 expected positive alpha, -1 negative
    description: str
    # Point-in-time field used for availability (fundamental factors).
    available_date_field: str = "ann_date"


@dataclass
class SingleFactorReport:
    """Summary of one factor's western-style tests."""

    factor: str
    rank_ic_mean: float | None = None
    rank_ic_ir: float | None = None
    ic_win_rate: float | None = None
    group_returns: dict[str, float] = field(default_factory=dict)
    decision: str = "pending"  # keep | watch | drop
    notes: str = ""


class SingleFactorTester:
    """Western Securities-style single-factor test skeleton.

    Pipeline (to implement once clean panels exist):
      1. preprocess: MAD clip -> zscore -> neutralize(industry, size)
      2. metrics: RankIC / ICIR, layered returns, optional bivariate & regression
      3. decision: keep / watch / drop with short rationale

    Project rule: every fundamental factor must pass through this tester
    before entering multi-factor aggregation or the MLP.
    """

    def __init__(self, cfg: dict[str, Any] | None = None) -> None:
        self.cfg = cfg or {}
        clean = (cfg or {}).get("clean", {})
        self.mad_n = float(clean.get("mad_n", 3.0))
        self.n_groups = int(self.cfg.get("factor_test", {}).get("n_groups", 10))

    def preprocess(self, factor: pd.Series, *, industry: pd.Series | None = None, size: pd.Series | None = None) -> pd.Series:
        """Cross-sectional MAD -> zscore -> optional neutralize. Placeholder."""
        raise NotImplementedError("Implement after clean factor panels are ready.")

    def calc_rank_ic(self, factor: pd.Series, forward_return: pd.Series) -> pd.Series:
        """Per-date RankIC series. Placeholder."""
        raise NotImplementedError

    def group_returns(self, factor: pd.Series, forward_return: pd.Series) -> pd.DataFrame:
        """Quantile portfolio returns. Placeholder."""
        raise NotImplementedError

    def run(self, spec: FactorSpec, factor: pd.Series, forward_return: pd.Series) -> SingleFactorReport:
        """Full single-factor battery for one FactorSpec. Placeholder."""
        raise NotImplementedError(
            f"Single-factor test for {spec.name} not implemented yet. "
            "See docs/single_factor_test.md"
        )
