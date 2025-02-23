"""Tests for TestBot implementation."""
import pytest
from buzzing.bots.test_bot import TestBot

@pytest.fixture
def test_bot():
    """Create a TestBot instance."""
    return TestBot()

@pytest.mark.asyncio
async def test_fetch(test_bot):
    """Test the fetch method."""
    result = await test_bot.fetch()
    assert result == "test successful"
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_fetch_now(test_bot):
    """Test the fetch_now method."""
    result = await test_bot.fetch_now()
    assert result == "test successful for now"
    assert isinstance(result, str)
