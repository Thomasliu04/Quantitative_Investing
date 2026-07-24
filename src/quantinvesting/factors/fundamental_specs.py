"""Starter list of fundamental factor candidates (CMS-inspired, Tushare-friendly).

Each entry is a learning unit: fill definition → compute PIT series → single-test
before any multi-factor / MLP usage.
"""

from __future__ import annotations

from quantinvesting.factors.single_test import FactorSpec

# First-batch fundamentals only — expand after single tests pass.
FUNDAMENTAL_CANDIDATES: list[FactorSpec] = [
    FactorSpec("bp_lf", "valuation", +1, "Book-to-price (1/PB), value"),
    FactorSpec("ep_ttm", "valuation", +1, "Earnings-to-price TTM (1/PE_TTM)"),
    FactorSpec("sp_ttm", "valuation", +1, "Sales-to-price TTM (1/PS_TTM)"),
    FactorSpec("dividend_yield_ttm", "valuation", +1, "Dividend yield TTM"),
    FactorSpec("roe_ttm", "growth", +1, "ROE TTM / profitability"),
    FactorSpec("roa_ttm", "growth", +1, "ROA TTM"),
    FactorSpec("roic_ttm", "growth", +1, "ROIC TTM"),
    FactorSpec("netprofit_yoy", "growth", +1, "Net profit YoY growth"),
    FactorSpec("ocfps", "cashflow", +1, "Operating cash flow per share"),
    FactorSpec("fcff_ttm", "cashflow", +1, "Free cash flow to firm TTM"),
]
