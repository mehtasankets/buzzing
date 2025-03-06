"""Bot implementation for fetching stock market data using Yahoo Finance API."""
import logging
from datetime import datetime
import requests
from buzzing.bots.bot_interface import BotInterface

logger = logging.getLogger(__name__)

class StockMarketBot(BotInterface):
    """Bot to fetch Sensex and Nifty data from Yahoo Finance."""

    def __init__(self):
        """Initialize the StockMarketBot."""
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.symbols = {
            "NIFTY": "^NSEI",  # Nifty 50 index
            "SENSEX": "^BSESN"  # BSE SENSEX
        }

    async def fetch(self) -> str:
        """Fetch stock market data on schedule.

        Returns:
            Formatted string with Sensex and Nifty values
        """
        return await self._get_market_data()

    async def fetch_now(self) -> str:
        """Fetch stock market data immediately on demand.

        Returns:
            Formatted string with current Sensex and Nifty values
        """
        return await self._get_market_data()

    async def _get_market_data(self) -> str:
        """Helper method to fetch and format market data from Yahoo Finance.

        Returns:
            Formatted string with market data
        """
        try:
            data = {}
            for name, symbol in self.symbols.items():
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                # Get the latest price
                meta = result.get('chart', {}).get('result', [{}])[0].get('meta', {})
                price = meta.get('regularMarketPrice', 'N/A')
                change = meta.get('regularMarketChangePercent', 0)
                change_symbol = '🔴' if change < 0 else '🟢'
                
                data[name] = {
                    'price': f"{price:,.2f}",
                    'change': f"{change:+.2f}%",
                    'symbol': change_symbol
                }
            
            return (
                f"🏢 Market Update ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n"
                f"SENSEX: {data['SENSEX']['symbol']} {data['SENSEX']['price']} ({data['SENSEX']['change']})\n"
                f"NIFTY: {data['NIFTY']['symbol']} {data['NIFTY']['price']} ({data['NIFTY']['change']})"
            )
        except Exception as e:
            error_msg = f"Error fetching market data: {str(e)}"
            logger.error(error_msg)
            return error_msg
