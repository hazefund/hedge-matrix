"""Unit tests for delta-neutral perpetual funding rate hedging."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hedge_matrix.models import AssetType, Holding, StrategyType
from hedge_matrix.hedging_engine import FundingHedgeEngine


def test_crypto_funding_hedge_evaluation():
    engine = FundingHedgeEngine(default_funding_apr=0.20)
    btc_holding = Holding(
        symbol="BTC",
        asset_type=AssetType.CRYPTO,
        quantity=1.0,
        cost_basis=60000.0,
        current_price=65000.0
    )

    rec = engine.evaluate_hedge(btc_holding)
    assert rec is not None
    assert rec.strategy_type == StrategyType.DELTA_NEUTRAL_FUNDING_HEDGE
    assert rec.projected_annual_yield_pct == 20.0
    assert rec.annualized_income_usd == 13000.0  # 65,000 * 20%
    assert rec.downside_protection_pct == 100.0
    assert rec.net_delta == 0.0


def test_equity_ignored_by_crypto_hedger():
    engine = FundingHedgeEngine()
    spy_holding = Holding(
        symbol="SPY",
        asset_type=AssetType.EQUITY,
        quantity=100.0,
        cost_basis=500.0,
        current_price=550.0
    )
    assert engine.evaluate_hedge(spy_holding) is None
