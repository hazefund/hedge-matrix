"""
Hybrid Yield Stacking Optimizer.
Combines base brokerage cash sweep, Options Wheel mechanics,
and perpetual funding rate arbitrage into a unified portfolio allocation.
"""

from typing import Optional

from .hedging_engine import FundingHedgeEngine
from .models import (
    AssetType,
    Holding,
    Portfolio,
    PortfolioAnalysis,
    StrategyRecommendation,
    StrategyType
)
from .wheel_engine import WheelStrategyEngine


class PortfolioOptimizer:
    def __init__(
        self,
        base_brokerage_rate: float = 0.048,  # 4.8% standard Treasury cash sweep
        funding_rate_apr: float = 0.18,       # 18% avg perp funding APR
        equity_iv: float = 0.28,              # 28% typical equity index IV
        crypto_iv: float = 0.55               # 55% typical crypto IV
    ):
        self.base_brokerage_rate = base_brokerage_rate
        self.funding_rate_apr = funding_rate_apr
        self.equity_iv = equity_iv
        self.crypto_iv = crypto_iv

        self.hedging_engine = FundingHedgeEngine(default_funding_apr=funding_rate_apr)
        self.wheel_engine = WheelStrategyEngine()

    def optimize(self, portfolio: Portfolio) -> PortfolioAnalysis:
        recommendations: list[StrategyRecommendation] = []
        total_income = 0.0
        hedged_value = 0.0

        # 1. Optimize Cash Component: Brokerage Cash Sweep + Wheel Cash-Secured Puts
        if portfolio.cash > 0:
            base_cash_income = portfolio.cash * self.base_brokerage_rate
            # Select target asset for CSP (e.g. SPY or dominant holding if available)
            target_sym = "SPY"
            target_price = 560.0
            if portfolio.holdings:
                largest_equity = max(
                    [h for h in portfolio.holdings if h.asset_type == AssetType.EQUITY],
                    key=lambda x: x.market_value,
                    default=None
                )
                if largest_equity:
                    target_sym = largest_equity.symbol
                    target_price = largest_equity.current_price

            csp_rec = self.wheel_engine.evaluate_cash_secured_put(
                available_cash=portfolio.cash,
                target_symbol=target_sym,
                target_price=target_price,
                implied_vol=self.equity_iv
            )

            # Combined Stacking: Cash interest + Put premium
            combined_cash_yield = (self.base_brokerage_rate + (csp_rec.projected_annual_yield_pct / 100.0)) * 100.0
            stacked_cash_income = portfolio.cash * (combined_cash_yield / 100.0)

            stacked_cash_rec = StrategyRecommendation(
                holding_symbol="USD / CASH",
                strategy_type=StrategyType.HYBRID_YIELD_STACK,
                strategy_name="Cash Yield Stacking: Brokerage Sweep + Cash-Secured Puts",
                actions=[
                    f"Earn {self.base_brokerage_rate * 100:.2f}% APY base interest on ${portfolio.cash:,.2f} in brokerage cash sweep/T-Bills.",
                    f"Simultaneously collateralize Cash-Secured Puts on {target_sym} at 7% OTM.",
                    f"Stack options premium (+{csp_rec.projected_annual_yield_pct:.1f}%) on top of risk-free cash yield.",
                    f"Achieve total projected yield of {combined_cash_yield:.1f}% APY on liquid capital."
                ],
                projected_annual_yield_pct=round(combined_cash_yield, 2),
                downside_protection_pct=7.0,
                net_delta=0.30,
                annualized_income_usd=round(stacked_cash_income, 2),
                capital_required=portfolio.cash,
                risk_summary="Low risk. Requires holding capital in margin-eligible interest-bearing securities."
            )
            recommendations.append(stacked_cash_rec)
            total_income += stacked_cash_income

        # 2. Optimize Crypto Holdings: Perpetual Funding Rate Basis Arbitrage
        for h in portfolio.holdings:
            if h.asset_type == AssetType.CRYPTO:
                rec = self.hedging_engine.evaluate_hedge(h, funding_apr=self.funding_rate_apr)
                if rec:
                    recommendations.append(rec)
                    total_income += rec.annualized_income_usd
                    hedged_value += h.market_value

        # 3. Optimize Equity Holdings: Options Wheel (Covered Calls)
        for h in portfolio.holdings:
            if h.asset_type == AssetType.EQUITY:
                rec = self.wheel_engine.evaluate_covered_call(h, implied_vol=self.equity_iv)
                if rec:
                    recommendations.append(rec)
                    total_income += rec.annualized_income_usd
                    hedged_value += h.market_value * 0.30  # partial downside buffer

        total_val = portfolio.total_portfolio_value
        optimized_yield_pct = (total_income / total_val * 100.0) if total_val > 0 else 0.0
        hedged_ratio_pct = (hedged_value / total_val * 100.0) if total_val > 0 else 0.0

        # Baseline unhedged yield assumption (e.g. ~1.5% dividends on equities + 0% on crypto + cash sweep)
        baseline_income = (portfolio.cash * self.base_brokerage_rate) + (portfolio.equity_value * 0.015)
        baseline_yield_pct = (baseline_income / total_val * 100.0) if total_val > 0 else 0.0

        return PortfolioAnalysis(
            portfolio=portfolio,
            recommendations=recommendations,
            baseline_unhedged_yield_pct=round(baseline_yield_pct, 2),
            optimized_hybrid_yield_pct=round(optimized_yield_pct, 2),
            total_projected_annual_income=round(total_income, 2),
            hedged_ratio_pct=round(hedged_ratio_pct, 1)
        )
