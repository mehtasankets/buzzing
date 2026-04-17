from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import requests

from buzzing.bots.bot_interface import BotInterface

LOG = logging.getLogger(__name__)


class StockMarketBot(BotInterface):
    """Fetches market snapshots for configured symbols using Yahoo Finance."""

    def __init__(self, symbols: Iterable[str] | None = None) -> None:
        self.symbols = list(symbols or ["^GSPC", "^DJI", "^IXIC"])
        self.base_url = "https://query1.finance.yahoo.com/v7/finance/quote"

    async def fetch(self) -> str:
        return await self._build_message()

    async def fetch_now(self) -> str:
        return await self._build_message()

    async def _build_message(self) -> str:
        payload = await self._get_market_data()
        if not payload:
            return "⚠️ Unable to fetch stock market data right now."

        quote_response = payload.get("quoteResponse", {})
        results = quote_response.get("result", [])
        if not isinstance(results, list) or not results:
            return "⚠️ No market data available for configured symbols."

        lines = [f"📈 Stock Market Snapshot ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})", ""]

        for quote in results:
            symbol = quote.get("symbol", "UNKNOWN")
            name = quote.get("shortName") or quote.get("longName") or symbol
            price = self._to_float(quote.get("regularMarketPrice"))
            change = self._to_float(quote.get("regularMarketChange"))
            change_pct = self._to_float(quote.get("regularMarketChangePercent"))

            if price is None:
                lines.append(f"• {name} ({symbol}): price unavailable")
                continue

            if change is None:
                change = 0.0
            if change_pct is None:
                change_pct = 0.0

            change_symbol = "🔻" if change < 0 else "🔺"
            lines.append(
                f"• {name} ({symbol}): ${price:,.2f} {change_symbol} {change:+.2f} ({change_pct:+.2f}%)"
            )

        return "\n".join(lines)

    async def _get_market_data(self) -> Dict[str, Any] | None:
        params = {"symbols": ",".join(self.symbols)}

        def _request() -> Dict[str, Any] | None:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else None

        try:
            return await asyncio.to_thread(_request)
        except requests.RequestException as exc:
            LOG.error("Failed to fetch market data: %s", exc)
            return None

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
