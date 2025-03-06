"""Tests for StockMarketBot."""
import pytest
from unittest.mock import patch, MagicMock
from buzzing.bots.stock_market_bot import StockMarketBot

@pytest.fixture
def market_bot():
    """Create a StockMarketBot instance."""
    return StockMarketBot()

@pytest.mark.asyncio
async def test_init():
    """Test initialization of StockMarketBot."""
    bot = StockMarketBot()
    
    # Check initial state
    assert "User-Agent" in bot.headers
    assert "NIFTY" in bot.symbols
    assert "SENSEX" in bot.symbols
    assert bot.symbols["NIFTY"] == "^NSEI"
    assert bot.symbols["SENSEX"] == "^BSESN"


@pytest.mark.asyncio
async def test_fetch_now(market_bot):
    """Test fetch_now method calls _get_market_data."""
    with patch.object(market_bot, '_get_market_data', return_value="Market data") as mock_get_data:
        result = await market_bot.fetch_now()
        mock_get_data.assert_called_once()
        assert result == "Market data"


@pytest.mark.asyncio
async def test_fetch(market_bot):
    """Test fetch method calls _get_market_data."""
    with patch.object(market_bot, '_get_market_data', return_value="Market data") as mock_get_data:
        result = await market_bot.fetch()
        mock_get_data.assert_called_once()
        assert result == "Market data"


@pytest.mark.asyncio
async def test_get_market_data_success(market_bot):
    """Test _get_market_data with successful API response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'chart': {
            'result': [
                {
                    'meta': {
                        'regularMarketPrice': 22000.5,
                        'regularMarketChangePercent': 1.25
                    }
                }
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        result = await market_bot._get_market_data()
        
        # Check that both symbols were queried
        assert mock_get.call_count == 2
        
        # Check that result contains expected data
        assert "Market Update" in result
        assert "SENSEX" in result
        assert "NIFTY" in result
        assert "22,000.50" in result  # Formatted price
        assert "+1.25%" in result     # Formatted change percent
        assert "🟢" in result         # Green indicator for positive change


@pytest.mark.asyncio
async def test_get_market_data_negative_change(market_bot):
    """Test _get_market_data with negative change percent."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'chart': {
            'result': [
                {
                    'meta': {
                        'regularMarketPrice': 22000.5,
                        'regularMarketChangePercent': -1.25
                    }
                }
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        result = await market_bot._get_market_data()
        
        # Check negative indicator
        assert "🔴" in result  # Red indicator for negative change
        assert "-1.25%" in result


@pytest.mark.asyncio
async def test_get_market_data_api_error(market_bot):
    """Test _get_market_data with API error."""
    with patch('requests.get', side_effect=Exception("API Error")) as mock_get:
        with patch('buzzing.bots.stock_market_bot.logger') as mock_logger:
            result = await market_bot._get_market_data()
            
            # Check error logging
            mock_logger.error.assert_called_once()
            assert "Error fetching market data" in mock_logger.error.call_args[0][0]
            
            # Check error response
            assert "Error fetching market data" in result
            assert "API Error" in result
