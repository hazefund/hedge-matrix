"""
Data models for HedgeMatrix portfolio management and strategy optimization.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AssetType(str, Enum):
    CRYPTO = "crypto"
    EQUITY = "equity"
    CASH = "cash"


class StrategyType(str, Enum):
    UNHEDGED_HOLD = "unhedged_hold"
    DELTA_NEUTRAL_FUNDING_HEDGE = "delta_neutral_funding_hedge"
    WHEEL_COVERED_CALL = "wheel_covered_call"
    WHEEL_CASH_SECURED_PUT = "wheel_cash_secured_put"
    HYBRID_YIELD_STACK = "hybrid_yield_stack"


@dataclass
class Holding:
    symbol: str
    asset_type: AssetType
    quantity: float
    cost_basis: float
    current_price: float

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_total(self) -> float:
        return self.quantity * self.cost_basis

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_total

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_total == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_total) * 100.0


@dataclass
class Portfolio:
    cash: float
    holdings: list[Holding] = field(default_factory=list)

    @property
    def total_holdings_value(self) -> float:
        return sum(h.market_value for h in self.holdings)

    @property
    def total_portfolio_value(self) -> float:
        return self.cash + self.total_holdings_value

    @property
    def crypto_value(self) -> float:
        return sum(h.market_value for h in self.holdings if h.asset_type == AssetType.CRYPTO)

    @property
    def equity_value(self) -> float:
        return sum(h.market_value for h in self.holdings if h.asset_type == AssetType.EQUITY)


@dataclass
class StrategyRecommendation:
    holding_symbol: str
    strategy_type: StrategyType
    strategy_name: str
    actions: list[str]
    projected_annual_yield_pct: float
    downside_protection_pct: float
    net_delta: float  # 0.0 = delta neutral, 1.0 = full long exposure
    annualized_income_usd: float
    capital_required: float
    risk_summary: str


@dataclass
class PortfolioAnalysis:
    portfolio: Portfolio
    recommendations: list[StrategyRecommendation]
    baseline_unhedged_yield_pct: float
    optimized_hybrid_yield_pct: float
    total_projected_annual_income: float
    hedged_ratio_pct: float
