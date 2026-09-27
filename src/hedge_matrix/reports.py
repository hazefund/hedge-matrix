"""
Reporting layer: Rich console output and HTML tear-sheet generator.
"""

import os
from typing import Optional

from .models import PortfolioAnalysis


def print_console_report(analysis: PortfolioAnalysis) -> None:
    p = analysis.portfolio
    print("╔══════════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                 🏛️  HedgeMatrix: Institutional Portfolio Optimization                    ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════════╝\n")

    print("════════════════════════════════════════════════════════════════════════════════════════════")
    print("  📊 PORTFOLIO COMPOSITION & ASSET ALLOCATION")
    print("════════════════════════════════════════════════════════════════════════════════════════════")
    print(f"  {'Symbol':<10} {'Type':<8} {'Qty':<12} {'Cost Basis':<14} {'Price':<14} {'Market Value':<16} {'PnL'}")
    print("  " + "─" * 88)
    for h in p.holdings:
        pnl_str = f"{h.unrealized_pnl_pct:+.1f}% (${h.unrealized_pnl:+,.0f})"
        print(f"  {h.symbol:<10} {h.asset_type.value:<8} {h.quantity:<12.4f} ${h.cost_basis:<13.2f} ${h.current_price:<13.2f} ${h.market_value:<15,.2f} {pnl_str}")

    if p.cash > 0:
        print(f"  {'USD CASH':<10} {'cash':<8} {'-':<12} {'-':<14} {'-':<14} ${p.cash:<15,.2f} -")

    print("  " + "─" * 88)
    print(f"  Total Portfolio Net Worth: ${p.total_portfolio_value:,.2f}  (Crypto: ${p.crypto_value:,.2f} | Equities: ${p.equity_value:,.2f} | Cash: ${p.cash:,.2f})\n")

    print("════════════════════════════════════════════════════════════════════════════════════════════")
    print("  📈 YIELD ENHANCEMENT & HEDGING STRATEGY MATRIX")
    print("════════════════════════════════════════════════════════════════════════════════════════════")
    print(f"  {'Asset':<12} {'Strategy':<32} {'Proj. Yield':<14} {'Protection':<14} {'Annual Income'}")
    print("  " + "─" * 88)

    for rec in analysis.recommendations:
        yield_str = f"{rec.projected_annual_yield_pct:.1f}% APY"
        prot_str = f"{rec.downside_protection_pct:.0f}% buffer"
        inc_str = f"+${rec.annualized_income_usd:,.2f}/yr"
        strat_display = rec.strategy_name[:30]
        print(f"  {rec.holding_symbol:<12} {strat_display:<32} {yield_str:<14} {prot_str:<14} {inc_str}")

    print("  " + "─" * 88)
    print(f"  ⚡ Baseline Unhedged Yield:  {analysis.baseline_unhedged_yield_pct:.2f}% / year")
    print(f"  🚀 Optimized Hybrid Yield:   {analysis.optimized_hybrid_yield_pct:.2f}% / year (Spread: +{analysis.optimized_hybrid_yield_pct - analysis.baseline_unhedged_yield_pct:.2f}%)")
    print(f"  💰 Projected Annual Income:   ${analysis.total_projected_annual_income:,.2f} / year")
    print(f"  🛡️ Portfolio Hedged Ratio:   {analysis.hedged_ratio_pct:.1f}%")
    print("════════════════════════════════════════════════════════════════════════════════════════════\n")

    print("📋 RECOMMENDED EXECUTION BLUEPRINT:")
    for i, rec in enumerate(analysis.recommendations, 1):
        print(f"\n  [{i}] {rec.strategy_name.upper()}")
        for act in rec.actions:
            print(f"      • {act}")
        print(f"      ⚠️  {rec.risk_summary}")
    print("")


def export_html_report(analysis: PortfolioAnalysis, output_path: str = "hedge_report.html") -> str:
    p = analysis.portfolio
    holdings_rows = "".join([
        f"""<tr>
            <td><b>{h.symbol}</b></td>
            <td><span class="badge {h.asset_type.value}">{h.asset_type.value.upper()}</span></td>
            <td>{h.quantity:,.4f}</td>
            <td>${h.cost_basis:,.2f}</td>
            <td>${h.current_price:,.2f}</td>
            <td><b>${h.market_value:,.2f}</b></td>
            <td style="color: {'#16a34a' if h.unrealized_pnl >= 0 else '#dc2626'}">{h.unrealized_pnl_pct:+.1f}% (${h.unrealized_pnl:+,.0f})</td>
        </tr>"""
        for h in p.holdings
    ])

    if p.cash > 0:
        holdings_rows += f"""<tr>
            <td><b>USD CASH</b></td>
            <td><span class="badge cash">CASH</span></td>
            <td>-</td><td>-</td><td>-</td>
            <td><b>${p.cash:,.2f}</b></td>
            <td>-</td>
        </tr>"""

    strat_cards = "".join([
        f"""<div class="card">
            <div class="card-header">
                <h3>{rec.strategy_name}</h3>
                <span class="yield-tag">+{rec.projected_annual_yield_pct:.1f}% APY</span>
            </div>
            <div class="card-body">
                <p><strong>Projected Annual Income:</strong> <span class="income-text">+${rec.annualized_income_usd:,.2f}/yr</span></p>
                <p><strong>Downside Protection:</strong> {rec.downside_protection_pct:.0f}% buffer | <strong>Net Delta:</strong> {rec.net_delta:.2f}</p>
                <ul class="action-list">
                    {''.join(f'<li>{act}</li>' for act in rec.actions)}
                </ul>
                <div class="risk-box"><strong>Risk Note:</strong> {rec.risk_summary}</div>
            </div>
        </div>"""
        for rec in analysis.recommendations
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HedgeMatrix Portfolio Optimization Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #ffffff; }}
        .header-box {{ background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 12px; padding: 25px; margin-bottom: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }}
        .stat-card {{ background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #38bdf8; }}
        .stat-card .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
        .stat-card .val {{ font-size: 24px; font-weight: bold; margin-top: 5px; color: #f8fafc; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #0f172a; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge.crypto {{ background: #818cf8; color: #0f172a; }}
        .badge.equity {{ background: #38bdf8; color: #0f172a; }}
        .badge.cash {{ background: #34d399; color: #0f172a; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; margin-bottom: 20px; padding: 20px; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 15px; }}
        .yield-tag {{ background: #15803d; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }}
        .income-text {{ color: #4ade80; font-size: 18px; font-weight: bold; }}
        .action-list {{ padding-left: 20px; line-height: 1.6; color: #cbd5e1; }}
        .risk-box {{ background: #0f172a; border-left: 4px solid #f59e0b; padding: 10px 15px; border-radius: 4px; font-size: 13px; color: #fbbf24; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-box">
            <h1>🏛️ HedgeMatrix: Portfolio Yield & Hedging Analysis</h1>
            <p style="color: #94a3b8;">Synthesizing Spot Holdings • Perpetual Funding Rate Arbitrage • The Options Wheel • Brokerage Cash Sweep</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">Total Net Worth</div>
                    <div class="val">${p.total_portfolio_value:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Optimized Hybrid Yield</div>
                    <div class="val" style="color: #4ade80;">{analysis.optimized_hybrid_yield_pct:.2f}%</div>
                </div>
                <div class="stat-card">
                    <div class="label">Projected Annual Income</div>
                    <div class="val" style="color: #38bdf8;">+${analysis.total_projected_annual_income:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Portfolio Hedged Ratio</div>
                    <div class="val">{analysis.hedged_ratio_pct:.1f}%</div>
                </div>
            </div>
        </div>

        <h2>Current Portfolio Holdings</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Cost Basis</th>
                    <th>Current Price</th>
                    <th>Market Value</th>
                    <th>Unrealized PnL</th>
                </tr>
            </thead>
            <tbody>
                {holdings_rows}
            </tbody>
        </table>

        <h2>Systematic Execution Blueprint</h2>
        {strat_cards}
    </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True) if os.path.dirname(output_path) else None
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
