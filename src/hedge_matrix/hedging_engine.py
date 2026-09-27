"""
Delta-neutral perpetual funding rate hedging engine.
Connects spot asset exposure with perpetual swap basis arbitrage.
"""

from typing import Optional

from .models import AssetType, Holding, StrategyRecommendation, StrategyType


class FundingHedgeEngine:
    def __init__(self, default_funding_apr: float = 0.18):
        """
        :param default_funding_apr: Estimated baseline annualized funding APR on perp shorts (default 18%).
        """
        self.default_funding_apr = default_funding_apr

    def evaluate_hedge(self, holding: Holding, funding_apr: Optional[float] = None) -> Optional[StrategyRecommendation]:
        """
        Evaluates a 1x Delta-Neutral Cash-and-Carry Hedge for spot crypto or synthetic proxy assets.
        """
        if holding.asset_type != AssetType.CRYPTO or holding.market_value <= 0:
            return None

        apr = funding_apr if funding_apr is not None else self.default_funding_apr
        market_val = holding.market_value
        annualized_income = market_val * apr

        actions = [
            f"Hold {holding.quantity:.4f} spot {holding.symbol} in cold custody or spot brokerage.",
            f"Open 1.0x Short Perpetual position for {holding.quantity:.4f} {holding.symbol} on Hyperliquid/dYdX.",
            "Lock in synthetic USD delta-neutral exposure (Net Delta = 0.0).",
            f"Harvest continuous hourly/8h funding payments projected at {apr * 100:.1f}% APR."
        ]

        risk_notes = (
            "Market Risk: Eliminated (100% hedged). "
            "Execution Risk: Counterparty venue risk & basis liquidation buffer. "
            "Maintain at least 25% margin buffer on short perp venue to avoid squeeze liquidation."
        )

        return StrategyRecommendation(
            holding_symbol=holding.symbol,
            strategy_type=StrategyType.DELTA_NEUTRAL_FUNDING_HEDGE,
            strategy_name=f"{holding.symbol} Delta-Neutral Basis & Funding Harvest",
            actions=actions,
            projected_annual_yield_pct=round(apr * 100, 2),
            downside_protection_pct=100.0,
            net_delta=0.0,
            annualized_income_usd=round(annualized_income, 2),
            capital_required=round(market_val * 1.25, 2),  # Spot value + 25% margin cushion
            risk_summary=risk_notes
        )
