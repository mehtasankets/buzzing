"""Tests for BotsInteractor."""
import pytest
import sqlite3
import asyncio
import telegram
from unittest.mock import MagicMock, patch, AsyncMock
from buzzing.bots_manager.bots_interactor import BotsInteractor
from buzzing.model.bot_config import BotConfig
from buzzing.bots.test_bot import TestBot

@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    
    # Create tables
    conn.execute('''
        CREATE TABLE bots_config(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            token TEXT,
            password TEXT,
            entry_module TEXT,
            entry_class TEXT,
            metadata TEXT,
            is_active BOOLEAN,
            cron TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE subscription(
            user_id INTEGER,
            username TEXT,
            bot_id INTEGER,
            is_active BOOLEAN,
            PRIMARY KEY (user_id, bot_id)
        )
    ''')
    
    # Insert test data
    conn.execute('''
        INSERT INTO bots_config (name, description, token, password, entry_module, entry_class, metadata, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test_bot', 'Test Bot', 'test_token', 'test_pass', 'buzzing.bots.test_bot', 'TestBot', '{}', 1))
    
    return conn

@pytest.fixture
def bots_interactor(db_connection):
    """Create a BotsInteractor instance."""
    return BotsInteractor(db_connection)

@pytest.mark.asyncio
async def test_bot_initialization(bots_interactor):
    """Test that bots are correctly initialized from database configurations."""
    # Create a mock application
    mock_app = AsyncMock()
    mock_app.__aenter__ = AsyncMock(return_value=mock_app)
    mock_app.__aexit__ = AsyncMock()
    mock_app.initialize = AsyncMock()
    mock_app.start = AsyncMock()
    mock_app.bot = AsyncMock()
    mock_app.bot.initialize = AsyncMock()
    mock_app.bot.delete_webhook = AsyncMock()
    mock_app.add_handler = AsyncMock()
    
    # Create a mock builder
    mock_builder = MagicMock()
    mock_builder.token.return_value = mock_builder
    mock_builder.build.return_value = mock_app
    
    with patch('telegram.ext.Application.builder', return_value=mock_builder), \
         patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Configure sleep to allow bot initialization
        mock_sleep.side_effect = [None, Exception('Stop loop')]
        
        try:
            # Start bot registration
            loop = await bots_interactor.register_bots()
            
            # Verify initialization sequence
            assert isinstance(loop, asyncio.AbstractEventLoop)
            assert len(bots_interactor.tasks) > 0
            assert mock_app.__aenter__.called
            assert mock_app.start.called
            assert mock_app.bot.delete_webhook.called
            
            # Verify initialization parameters
            mock_app.bot.delete_webhook.assert_called_with(drop_pending_updates=True)
        except Exception as e:
            # We expect the sleep exception
            assert str(e) == 'Stop loop'

@pytest.mark.asyncio
async def test_bot_polling_task(bots_interactor):
    """Test that bot polling task is created and runs correctly."""
    # Create a mock application
    mock_app = AsyncMock()
    mock_app.__aenter__ = AsyncMock(return_value=mock_app)
    mock_app.__aexit__ = AsyncMock()
    mock_app.initialize = AsyncMock()
    mock_app.start = AsyncMock()
    mock_app.bot = AsyncMock()
    mock_app.bot.initialize = AsyncMock()
    mock_app.bot.delete_webhook = AsyncMock()
    mock_app.updater = AsyncMock()
    mock_app.updater.start_polling = AsyncMock()
    mock_app.add_handler = AsyncMock()
    
    # Create a mock builder
    mock_builder = MagicMock()
    mock_builder.token.return_value = mock_builder
    mock_builder.build.return_value = mock_app
    
    with patch('telegram.ext.Application.builder', return_value=mock_builder):
        # Start bot registration
        await bots_interactor.register_bots()
        
        # Get the created task
        assert len(bots_interactor.tasks) == 1
        bot_task = bots_interactor.tasks[0]
        
        # Verify task is running
        assert not bot_task.done()
        assert not bot_task.cancelled()
        
        # Stop the bot
        await bots_interactor.stop_bots()
        
        # Verify task is properly cleaned up
        assert bot_task.done() or bot_task.cancelled()

@pytest.mark.asyncio
async def test_stop_bots(bots_interactor):
    """Test stopping all bots."""
    # Create a mock application
    mock_app = AsyncMock()
    mock_app.__aenter__ = AsyncMock(return_value=mock_app)  # Return self from __aenter__
    mock_app.__aexit__ = AsyncMock()
    mock_app.initialize = AsyncMock()
    mock_app.start = AsyncMock()
    mock_app.stop = AsyncMock()
    mock_app.bot = AsyncMock()
    mock_app.bot.initialize = AsyncMock()
    mock_app.bot.delete_webhook = AsyncMock()
    mock_app.updater = AsyncMock()
    mock_app.updater.start_polling = AsyncMock()
    mock_app.updater.stop = AsyncMock()
    mock_app.add_handler = AsyncMock()
    
    # Make sure all mocks return None by default
    mock_app.add_handler.return_value = None
    mock_app.start.return_value = None
    mock_app.bot.delete_webhook.return_value = None
    mock_app.updater.start_polling.return_value = None
    
    # Create a mock builder
    mock_builder = MagicMock()
    mock_builder.token.return_value = mock_builder
    mock_builder.build.return_value = mock_app
    
    with patch('telegram.ext.Application.builder', return_value=mock_builder), \
         patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Make sleep raise an exception to break the loop
        mock_sleep.side_effect = Exception('Stop loop')
        
        try:
            # Register bots
            await bots_interactor.register_bots()
            
            # Stop bots
            await bots_interactor.stop_bots()
            
            # Verify bot was stopped
            assert mock_app.stop.called
            
            # Verify all tasks are done
            for task in bots_interactor.tasks:
                assert task.cancelled() or task.done()
        except Exception as e:
            # We expect an exception from asyncio.sleep
            assert str(e) == 'Stop loop'

@pytest.mark.asyncio
async def test_register_bots_with_invalid_config(db_connection):
    """Test registering bots with invalid configuration."""
    # Insert invalid bot config
    db_connection.execute('''
        INSERT INTO bots_config (name, description, token, password, entry_module, entry_class, metadata, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('invalid_bot', 'Invalid Bot', 'invalid_token', 'test_pass', 'nonexistent.module', 'NonexistentClass', '{}', 1))
    
    bots_interactor = BotsInteractor(db_connection)
    
    # Create a mock application that fails on token validation
    mock_builder = MagicMock()
    mock_builder.token.side_effect = telegram.error.InvalidToken('Invalid token')
    
    with patch('telegram.ext.Application.builder', return_value=mock_builder):
        # Should raise InvalidToken during initialization
        with pytest.raises(telegram.error.InvalidToken) as exc_info:
            await bots_interactor.register_bots()
        
        # Verify the error message
        assert str(exc_info.value) == 'Invalid token'
        
        # No tasks should be registered due to error
        assert len(bots_interactor.tasks) == 0
