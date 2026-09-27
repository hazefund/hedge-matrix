"""
Command-Line Interface (CLI) for HedgeMatrix.
"""

import argparse
import sys

from .models import AssetType, Holding, Portfolio
from .optimizer import PortfolioOptimizer
from .parsers import parse_portfolio_file
from .reports import print_console_report, export_html_report


def run_demo(args: argparse.Namespace) -> int:
    demo_portfolio = Portfolio(
        cash=50000.0,
        holdings=[
            Holding(symbol="BTC", asset_type=AssetType.CRYPTO, quantity=1.5, cost_basis=58000.0, current_price=64500.0),
            Holding(symbol="ETH", asset_type=AssetType.CRYPTO, quantity=12.0, cost_basis=2400.0, current_price=2650.0),
            Holding(symbol="SOL", asset_type=AssetType.CRYPTO, quantity=80.0, cost_basis=130.0, current_price=155.0),
            Holding(symbol="SPY", asset_type=AssetType.EQUITY, quantity=100.0, cost_basis=510.0, current_price=570.0),
            Holding(symbol="NVDA", asset_type=AssetType.EQUITY, quantity=150.0, cost_basis=110.0, current_price=125.0),
            Holding(symbol="AAPL", asset_type=AssetType.EQUITY, quantity=100.0, cost_basis=195.0, current_price=228.0),
        ]
    )

    optimizer = PortfolioOptimizer(
        base_brokerage_rate=args.base_rate,
        funding_rate_apr=args.funding_apr
    )
    analysis = optimizer.optimize(demo_portfolio)
    print_console_report(analysis)

    if args.html:
        export_html_report(analysis, output_path=args.html)
        print(f"✅ Interactive HTML Tear-Sheet exported to: {args.html}\n")
    return 0


def run_analyze(args: argparse.Namespace) -> int:
    try:
        portfolio = parse_portfolio_file(args.file)
    except Exception as e:
        print(f"❌ Failed to parse portfolio document '{args.file}': {e}", file=sys.stderr)
        return 1

    optimizer = PortfolioOptimizer(
        base_brokerage_rate=args.base_rate,
        funding_rate_apr=args.funding_apr
    )
    analysis = optimizer.optimize(portfolio)
    print_console_report(analysis)

    if args.html:
        export_html_report(analysis, output_path=args.html)
        print(f"✅ Interactive HTML Tear-Sheet exported to: {args.html}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HedgeMatrix: Portfolio Hedging & Hybrid Yield Optimizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze and optimize an uploaded portfolio file (CSV/JSON)")
    analyze_parser.add_argument("file", help="Path to portfolio CSV or JSON export")
    analyze_parser.add_argument("--base-rate", type=float, default=0.048, help="Base brokerage cash sweep APY (default: 0.048)")
    analyze_parser.add_argument("--funding-apr", type=float, default=0.18, help="Estimated perp short funding APR (default: 0.18)")
    analyze_parser.add_argument("--html", default=None, help="Optional output path to export HTML tear-sheet")

    # demo
    demo_parser = subparsers.add_parser("demo", help="Run instant optimization on a realistic multi-asset sample portfolio")
    demo_parser.add_argument("--base-rate", type=float, default=0.048, help="Base brokerage cash sweep APY")
    demo_parser.add_argument("--funding-apr", type=float, default=0.18, help="Estimated perp short funding APR")
    demo_parser.add_argument("--html", default="demo_hedge_report.html", help="Path to export HTML tear-sheet")

    args = parser.parse_args()

    if args.subcommand == "analyze":
        return run_analyze(args)
    elif args.subcommand == "demo":
        return run_demo(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
