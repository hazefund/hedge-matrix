"""Unit tests for the Options Wheel strategy engine."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hedge_matrix.models import AssetType, Holding, StrategyType
from hedge_matrix.wheel_engine import WheelStrategyEngine


def test_covered_call_evaluation():
    engine = WheelStrategyEngine(target_otm_pct=0.07, target_dte=30)
    aapl_holding = Holding(
        symbol="AAPL",
        asset_type=AssetType.EQUITY,
        quantity=100.0,
        cost_basis=200.0,
        current_price=220.0
    )

    rec = engine.evaluate_covered_call(aapl_holding, implied_vol=0.30)
    assert rec is not None
    assert rec.strategy_type == StrategyType.WHEEL_COVERED_CALL
    assert rec.projected_annual_yield_pct > 0.0
    assert rec.annualized_income_usd > 0.0
    assert rec.capital_required == 22000.0


def test_cash_secured_put_evaluation():
    engine = WheelStrategyEngine(target_otm_pct=0.07, target_dte=30)
    rec = engine.evaluate_cash_secured_put(
        available_cash=50000.0,
        target_symbol="SPY",
        target_price=560.0,
        implied_vol=0.25
    )
    assert rec is not None
    assert rec.strategy_type == StrategyType.WHEEL_CASH_SECURED_PUT
    assert rec.capital_required == 50000.0
    assert rec.annualized_income_usd > 0.0
