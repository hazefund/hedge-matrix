"""
Options Wheel Strategy Engine.
Evaluates systematic Cash-Secured Puts (CSP) and Covered Calls (CC).
"""

from typing import Optional

from .models import AssetType, Holding, StrategyRecommendation, StrategyType


class WheelStrategyEngine:
    def __init__(self, target_otm_pct: float = 0.07, target_dte: int = 30):
        """
        :param target_otm_pct: Target out-of-the-money distance (default 7% OTM).
        :param target_dte: Days to expiration for rolling contracts (default 30 DTE).
        """
        self.target_otm_pct = target_otm_pct
        self.target_dte = target_dte

    def evaluate_covered_call(self, holding: Holding, implied_vol: float = 0.35) -> Optional[StrategyRecommendation]:
        """
        Evaluates a systematic Covered Call overlay on existing spot holdings.
        """
        if holding.market_value <= 0:
            return None

        # Estimated 30-day 7% OTM call option premium based on volatility approximation
        # Premium ~ Spot * (IV * sqrt(DTE/365)) * 0.4 (delta ~ 0.25-0.30 approximation)
        dte_factor = (self.target_dte / 365.0) ** 0.5
        est_monthly_yield = implied_vol * dte_factor * 0.35
        est_annual_yield = est_monthly_yield * 12.0

        strike_price = round(holding.current_price * (1.0 + self.target_otm_pct), 2)
        annualized_income = holding.market_value * est_annual_yield

        actions = [
            f"Retain {holding.quantity:.2f} shares/units of {holding.symbol} as underlying collateral.",
            f"Sell 30-45 DTE Covered Calls at ${strike_price} strike (~{self.target_otm_pct * 100:.0f}% Out-of-the-Money).",
            f"Harvest option theta decay (est. ~{est_monthly_yield * 100:.2f}% monthly premium).",
            "If spot exceeds strike at expiration: Realize capital appreciation up to strike plus retain all collected premium."
        ]

        risk_notes = (
            f"Downside Protection: ~{est_monthly_yield * 100:.1f}% monthly buffer from premium. "
            f"Upside Cap: Capped at ${strike_price} strike. "
            "Net Delta: ~0.70 (Bullish/Neutral bias)."
        )

        return StrategyRecommendation(
            holding_symbol=holding.symbol,
            strategy_type=StrategyType.WHEEL_COVERED_CALL,
            strategy_name=f"{holding.symbol} Options Wheel (Covered Call Leg)",
            actions=actions,
            projected_annual_yield_pct=round(est_annual_yield * 100, 2),
            downside_protection_pct=round(est_monthly_yield * 100 * 2, 2),
            net_delta=0.70,
            annualized_income_usd=round(annualized_income, 2),
            capital_required=holding.market_value,
            risk_summary=risk_notes
        )

    def evaluate_cash_secured_put(self, available_cash: float, target_symbol: str, target_price: float,
                                 implied_vol: float = 0.35) -> Optional[StrategyRecommendation]:
        """
        Evaluates a Cash-Secured Put (CSP) on available idle cash balance.
        """
        if available_cash < 1000:
            return None

        strike_price = round(target_price * (1.0 - self.target_otm_pct), 2)
        dte_factor = (self.target_dte / 365.0) ** 0.5
        est_monthly_yield = implied_vol * dte_factor * 0.35
        est_annual_yield = est_monthly_yield * 12.0

        annualized_income = available_cash * est_annual_yield

        actions = [
            f"Maintain ${available_cash:,.2f} collateral in base brokerage account earning cash sweep interest.",
            f"Sell 30-45 DTE Cash-Secured Puts on {target_symbol} at ${strike_price} strike (~{self.target_otm_pct * 100:.0f}% OTM).",
            f"Capture premium decay (est. ~{est_monthly_yield * 100:.2f}% monthly yield).",
            f"If assigned: Acquire {target_symbol} at effective net price of ~${strike_price * (1.0 - est_monthly_yield):.2f}, then transition to Covered Calls."
        ]

        risk_notes = (
            f"Entry Discount: Effectively enters {target_symbol} at ~{self.target_otm_pct * 100:.0f}% discount. "
            "Assignment Risk: Must purchase shares if price drops below strike at expiry."
        )

        return StrategyRecommendation(
            holding_symbol=target_symbol,
            strategy_type=StrategyType.WHEEL_CASH_SECURED_PUT,
            strategy_name=f"{target_symbol} Options Wheel (Cash-Secured Put Leg)",
            actions=actions,
            projected_annual_yield_pct=round(est_annual_yield * 100, 2),
            downside_protection_pct=round(self.target_otm_pct * 100, 2),
            net_delta=0.30,
            annualized_income_usd=round(annualized_income, 2),
            capital_required=available_cash,
            risk_summary=risk_notes
        )
