"""Tests for BotConfig model."""
import dataclasses
import pytest
from buzzing.model.bot_config import BotConfig
from buzzing.bots.test_bot import TestBot

@pytest.fixture
def test_bot():
    """Create a test bot instance."""
    return TestBot()

@pytest.fixture
def bot_config(test_bot):
    """Create a test bot configuration."""
    return BotConfig(
        id=1,
        name="test_bot",
        description="Test bot for unit tests",
        token="test_token",
        password="test_password",
        bot=test_bot,
        metadata={"test_key": "test_value"},
        is_active=True
    )

def test_bot_config_creation(bot_config):
    """Test bot configuration creation."""
    assert bot_config.id == 1
    assert bot_config.name == "test_bot"
    assert bot_config.description == "Test bot for unit tests"
    assert bot_config.token == "test_token"
    assert bot_config.password == "test_password"
    assert isinstance(bot_config.bot, TestBot)
    assert bot_config.metadata == {"test_key": "test_value"}
    assert bot_config.is_active is True

def test_bot_config_immutability(bot_config):
    """Test that BotConfig is immutable."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        bot_config.name = "new_name"
