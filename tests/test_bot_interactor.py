"""Tests for BotInteractor."""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call
from telegram import Update
from telegram.ext import Application, CallbackContext
from buzzing.bots_manager.bot_interactor import BotInteractor
from buzzing.model.bot_config import BotConfig
from buzzing.model.subscription import Subscription
from buzzing.bots.test_bot import TestBot
from buzzing.util.cron_scheduler import CronScheduler

@pytest.fixture
def bot_config():
    """Create a test bot configuration."""
    return BotConfig(
        id=1,
        name="test_bot",
        description="Test bot for unit tests",
        token="test_token",
        password="test_password",
        bot=TestBot(),
        metadata={"test_key": "test_value"},
        is_active=True,
        cron=None
    )

@pytest.fixture
def bot_config_with_cron():
    """Create a test bot configuration with cron schedule."""
    return BotConfig(
        id=2,
        name="test_bot_with_cron",
        description="Test bot with cron for unit tests",
        token="test_token_cron",
        password="test_password",
        bot=TestBot(),
        metadata={"test_key": "test_value"},
        is_active=True,
        cron="*/5 * * * *"
    )

@pytest.fixture
def dao():
    """Create a mock DAO."""
    mock_dao = MagicMock()
    mock_dao.fetch_all_subscriptions.return_value = []
    return mock_dao

@pytest.fixture
def mock_update():
    """Create a mock Update object."""
    update = MagicMock(spec=Update)
    update.effective_user.id = 123456789
    update.effective_user.username = "test_user"
    update.message.text = "/start test_password"
    update.message.reply_text = AsyncMock()
    update.message.reply_html = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    """Create a mock Context object."""
    return MagicMock(spec=CallbackContext)

@pytest.fixture
def bot_interactor(bot_config, dao, mock_update):
    """Create a BotInteractor instance."""
    # Create a subscription for the test user
    subscriptions = [Subscription(mock_update.effective_user.id, mock_update.effective_user.username, bot_config.id, True)]
    return BotInteractor(bot_config, subscriptions, dao)

@pytest.fixture
def bot_interactor_with_cron(bot_config_with_cron, dao, mock_update):
    """Create a BotInteractor instance with cron scheduling."""
    # Create a subscription for the test user
    subscriptions = [Subscription(mock_update.effective_user.id, mock_update.effective_user.username, bot_config_with_cron.id, True)]
    return BotInteractor(bot_config_with_cron, subscriptions, dao)

@pytest.mark.asyncio
async def test_start_command(bot_interactor, mock_update, mock_context):
    """Test the /start command handler."""
    # Test start command
    await bot_interactor.start(mock_update, mock_context)
    
    # Verify message was sent
    mock_update.message.reply_html.assert_called_once()
    assert "Welcome" in mock_update.message.reply_html.call_args[0][0]

@pytest.mark.asyncio
async def test_help_command(bot_interactor, mock_update, mock_context):
    """Test the /help command handler."""
    await bot_interactor.help(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert "commands" in mock_update.message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_fetch_now_command(bot_interactor, mock_update, mock_context):
    """Test the /fetchnow command handler."""
    # Mock fetch_now to return test data
    test_data = "test successful"
    bot_interactor.config.bot.fetch_now = AsyncMock(return_value=test_data)
    
    await bot_interactor.fetch_now(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert test_data in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_stop_command(bot_interactor, mock_update, mock_context):
    """Test the /stop command handler."""
    await bot_interactor.stop(mock_update, mock_context)
    
    mock_update.message.reply_html.assert_called_once()
    assert "sad to see you go" in mock_update.message.reply_html.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_invalid_password(bot_interactor, mock_update, mock_context):
    """Test start command with invalid password."""
    # Set wrong password
    mock_update.message.text = "/start wrong_password"
    
    # Test start command
    await bot_interactor.start(mock_update, mock_context)
    
    # Verify welcome message was sent
    mock_update.message.reply_html.assert_called_once()
    assert "enter password" in mock_update.message.reply_html.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_fetch_now_error_handling(bot_interactor, mock_update, mock_context):
    """Test error handling in fetch_now command."""
    # Mock bot.fetch_now to raise an exception
    bot_interactor.config.bot.fetch_now = MagicMock(side_effect=Exception("Test error"))
    
    await bot_interactor.fetch_now(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert "something went wrong" in mock_update.message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_fetch_now_unauthenticated(bot_interactor, mock_update, mock_context):
    """Test fetch_now command with unauthenticated user."""
    # Remove user from subscriptions
    bot_interactor.subscriptions = []
    
    await bot_interactor.fetch_now(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert "authenticate first" in mock_update.message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_fetch_method(bot_interactor):
    """Test the fetch method."""
    # Mock bot.fetch to return test data
    test_data = "Test fetch data"
    bot_interactor.config.bot.fetch = AsyncMock(return_value=test_data)
    
    # Mock the bot instance
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()
    bot_interactor.application.bot = mock_bot
    
    # Add a subscription for testing
    bot_interactor.subscriptions = [Subscription(123456789, "test_user", bot_interactor.config.id, True)]
    
    # Call fetch method
    await bot_interactor.fetch()
    
    # Verify bot.fetch was called
    assert bot_interactor.config.bot.fetch.await_count == 1
    
    # Verify message was sent to subscriber
    assert mock_bot.send_message.await_count == 1
    await_args = mock_bot.send_message.await_args
    assert await_args is not None
    assert await_args.args == (123456789, test_data)

@pytest.mark.asyncio
async def test_stop_polling_error_handling(bot_interactor):
    """Test error handling in stop_polling method."""
    # Mock application methods to raise exceptions
    bot_interactor.application.updater.stop = AsyncMock(side_effect=RuntimeError("Test error"))
    bot_interactor.application.stop = AsyncMock(side_effect=RuntimeError("Test error"))
    
    # Should not raise exception
    await bot_interactor.stop_polling()
    
    # Verify stop was attempted
    assert bot_interactor.stop_bot == True

@pytest.mark.asyncio
async def test_initiate_error_handling(bot_interactor):
    """Test error handling in initiate method."""
    # Mock application methods to raise exceptions
    bot_interactor.application.initialize = AsyncMock(side_effect=Exception("Test error"))
    
    with pytest.raises(Exception):
        await bot_interactor.initiate()

@pytest.mark.asyncio
async def test_cancel_command(bot_interactor, mock_update, mock_context):
    """Test the cancel command handler."""
    await bot_interactor.cancel(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert "bye" in mock_update.message.reply_text.call_args[0][0].lower()
