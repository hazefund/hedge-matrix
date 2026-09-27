"""
Document and portfolio file parsers.
Supports CSV, JSON, and common brokerage export schemas.
"""

import csv
import json
import os
from typing import Any

from .models import AssetType, Holding, Portfolio

KNOWN_CRYPTO = {
    "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOGE", "DOT", "LINK",
    "MATIC", "NEAR", "SAGA", "GMX", "WLD", "GRASS", "DYDX", "HYPER", "PURR"
}

KNOWN_CASH = {"USD", "USDC", "USDT", "CASH", "EUR", "GBP"}


def infer_asset_type(symbol: str, raw_type: str = "") -> AssetType:
    sym = symbol.upper().strip()
    if raw_type.lower() in ("crypto", "cryptocurrency"):
        return AssetType.CRYPTO
    if raw_type.lower() in ("equity", "stock", "etf"):
        return AssetType.EQUITY
    if raw_type.lower() in ("cash", "fiat", "stablecoin"):
        return AssetType.CASH

    if sym in KNOWN_CASH or sym.startswith("USD"):
        return AssetType.CASH
    if sym in KNOWN_CRYPTO or "-PERP" in sym or "-USD" in sym:
        return AssetType.CRYPTO
    return AssetType.EQUITY


def parse_portfolio_file(file_path: str) -> Portfolio:
    """Parse portfolio from CSV or JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Portfolio document not found at: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    if ext == ".json":
        return _parse_json(file_path)
    else:
        return _parse_csv(file_path)


def _parse_csv(file_path: str) -> Portfolio:
    holdings: list[Holding] = []
    cash = 0.0

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}

            symbol = (
                normalized_row.get("symbol") or
                normalized_row.get("ticker") or
                normalized_row.get("asset") or ""
            ).upper()

            if not symbol:
                continue

            raw_type = normalized_row.get("type", "")
            asset_type = infer_asset_type(symbol, raw_type)

            qty = float(
                normalized_row.get("quantity") or
                normalized_row.get("shares") or
                normalized_row.get("qty") or 0.0
            )

            cost = float(
                normalized_row.get("cost_basis") or
                normalized_row.get("cost") or
                normalized_row.get("avg_price") or 0.0
            )

            price = float(
                normalized_row.get("current_price") or
                normalized_row.get("price") or
                normalized_row.get("mark_price") or cost
            )

            if asset_type == AssetType.CASH:
                cash += qty * price if price > 0 else qty
            else:
                holdings.append(Holding(
                    symbol=symbol,
                    asset_type=asset_type,
                    quantity=qty,
                    cost_basis=cost,
                    current_price=price
                ))

    return Portfolio(cash=cash, holdings=holdings)


def _parse_json(file_path: str) -> Portfolio:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cash = float(data.get("cash", 0.0))
    holdings: list[Holding] = []

    for item in data.get("holdings", []):
        symbol = str(item.get("symbol", "")).upper()
        asset_type = infer_asset_type(symbol, item.get("type", ""))
        qty = float(item.get("quantity", 0.0))
        cost = float(item.get("cost_basis", 0.0))
        price = float(item.get("current_price", cost))

        if asset_type == AssetType.CASH:
            cash += qty * price if price > 0 else qty
        else:
            holdings.append(Holding(
                symbol=symbol,
                asset_type=asset_type,
                quantity=qty,
                cost_basis=cost,
                current_price=price
            ))

    return Portfolio(cash=cash, holdings=holdings)
