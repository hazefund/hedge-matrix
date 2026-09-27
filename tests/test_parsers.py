"""Unit tests for portfolio parsers."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hedge_matrix.models import AssetType
from hedge_matrix.parsers import infer_asset_type, parse_portfolio_file


def test_infer_asset_type():
    assert infer_asset_type("BTC") == AssetType.CRYPTO
    assert infer_asset_type("ETH") == AssetType.CRYPTO
    assert infer_asset_type("SPY") == AssetType.EQUITY
    assert infer_asset_type("USD") == AssetType.CASH
    assert infer_asset_type("CUSTOM", raw_type="crypto") == AssetType.CRYPTO


def test_parse_csv_portfolio():
    csv_data = """symbol,quantity,cost_basis,current_price
BTC,2.0,50000,60000
AAPL,50,150,200
USD,10000,1,1
"""
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w+", delete=False) as tmp:
        tmp.write(csv_data)
        tmp.flush()
        tmp_name = tmp.name

    try:
        portfolio = parse_portfolio_file(tmp_name)
        assert portfolio.cash == 10000.0
        assert len(portfolio.holdings) == 2

        btc = next(h for h in portfolio.holdings if h.symbol == "BTC")
        assert btc.quantity == 2.0
        assert btc.market_value == 120000.0
        assert btc.unrealized_pnl == 20000.0
        assert btc.asset_type == AssetType.CRYPTO

        aapl = next(h for h in portfolio.holdings if h.symbol == "AAPL")
        assert aapl.market_value == 10000.0
        assert aapl.asset_type == AssetType.EQUITY
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
