"""Unit tests for the PortfolioOptimizer and yield stacking."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hedge_matrix.models import AssetType, Holding, Portfolio
from hedge_matrix.optimizer import PortfolioOptimizer


def test_hybrid_yield_optimization():
    portfolio = Portfolio(
        cash=25000.0,
        holdings=[
            Holding(symbol="BTC", asset_type=AssetType.CRYPTO, quantity=1.0, cost_basis=60000.0, current_price=60000.0),
            Holding(symbol="SPY", asset_type=AssetType.EQUITY, quantity=50.0, cost_basis=500.0, current_price=500.0),
        ]
    )

    optimizer = PortfolioOptimizer(base_brokerage_rate=0.05, funding_rate_apr=0.20)
    analysis = optimizer.optimize(portfolio)

    assert analysis.total_projected_annual_income > 0.0
    assert analysis.optimized_hybrid_yield_pct > analysis.baseline_unhedged_yield_pct
    assert len(analysis.recommendations) >= 3  # Cash stack, BTC hedge, SPY covered call
    assert analysis.hedged_ratio_pct > 0.0
