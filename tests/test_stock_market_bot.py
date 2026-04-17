import pytest
from unittest.mock import MagicMock, patch

from buzzing.bots.stock_market_bot import StockMarketBot


@pytest.mark.asyncio
async def test_fetch_formats_up_and_down_symbols() -> None:
    bot = StockMarketBot(symbols=["A", "B"])

    payload = {
        "quoteResponse": {
            "result": [
                {
                    "symbol": "A",
                    "shortName": "Alpha",
                    "regularMarketPrice": 100.0,
                    "regularMarketChange": 1.5,
                    "regularMarketChangePercent": 1.52,
                },
                {
                    "symbol": "B",
                    "shortName": "Beta",
                    "regularMarketPrice": 50.0,
                    "regularMarketChange": -0.5,
                    "regularMarketChangePercent": -0.99,
                },
            ]
        }
    }

    with patch.object(bot, "_get_market_data", return_value=payload):
        result = await bot.fetch_now()

    assert "Alpha" in result
    assert "Beta" in result
    assert "🔺" in result
    assert "🔻" in result


@pytest.mark.asyncio
async def test_fetch_handles_missing_price() -> None:
    bot = StockMarketBot(symbols=["A"])
    payload = {"quoteResponse": {"result": [{"symbol": "A", "shortName": "Alpha"}]}}

    with patch.object(bot, "_get_market_data", return_value=payload):
        result = await bot.fetch()

    assert "price unavailable" in result


@pytest.mark.asyncio
async def test_get_market_data_handles_http_error() -> None:
    bot = StockMarketBot(symbols=["A"])

    with patch("buzzing.bots.stock_market_bot.requests.get", side_effect=__import__("requests").RequestException("boom")):
        result = await bot._get_market_data()

    assert result is None
