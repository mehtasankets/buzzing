"""Tests for the driver module."""
import os
import pytest
import logging
import asyncio
import sqlite3
from unittest.mock import MagicMock, AsyncMock, patch
from buzzing.driver import main, setup_logger
from buzzing.bots_manager.bots_interactor import BotsInteractor

@pytest.fixture
def mock_bots_interactor():
    """Create a mock BotsInteractor."""
    mock = MagicMock(spec=BotsInteractor)
    mock.register_bots = AsyncMock()
    mock.stop_bots = AsyncMock()
    mock.tasks = []
    return mock

@pytest.mark.asyncio
async def test_main_success(mock_bots_interactor, tmp_path):
    """Test successful execution of main function."""
    # Set up test database path
    db_path = str(tmp_path / "test.db")
    os.environ["BUZZING_DB_PATH"] = db_path
    
    # Mock BotsInteractor
    with patch("buzzing.driver.BotsInteractor", return_value=mock_bots_interactor):
        # Mock event loop
        mock_loop = MagicMock()
        mock_loop.add_signal_handler = MagicMock()
        mock_bots_interactor.register_bots.return_value = mock_loop
        
        # Run main
        await main()
        
        # Verify BotsInteractor was initialized and used correctly
        mock_bots_interactor.register_bots.assert_called_once()
        assert mock_loop.add_signal_handler.call_count == 2  # SIGTERM and SIGINT

@pytest.mark.asyncio
async def test_main_database_error(mock_bots_interactor):
    """Test main function with database connection error."""
    # Set invalid database path
    os.environ["BUZZING_DB_PATH"] = "/nonexistent/path/db.sqlite"
    
    with pytest.raises(Exception):
        await main()

@pytest.mark.asyncio
async def test_main_bot_error(mock_bots_interactor, tmp_path):
    """Test main function with bot registration error."""
    # Set up test database path
    db_path = str(tmp_path / "test.db")
    os.environ["BUZZING_DB_PATH"] = db_path
    
    # Mock BotsInteractor to raise an error
    with patch("buzzing.driver.BotsInteractor", return_value=mock_bots_interactor):
        mock_bots_interactor.register_bots.side_effect = Exception("Bot registration failed")
        
        with pytest.raises(Exception) as exc_info:
            await main()
        assert "Bot registration failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_main_task_error(mock_bots_interactor, tmp_path):
    """Test main function with bot task error."""
    # Set up test database path
    db_path = str(tmp_path / "test.db")
    os.environ["BUZZING_DB_PATH"] = db_path
    
    # Mock BotsInteractor with a failing task
    with patch("buzzing.driver.BotsInteractor", return_value=mock_bots_interactor):
        # Create a failing task
        async def failing_task():
            raise Exception("Task failed")
        
        mock_loop = MagicMock()
        mock_loop.add_signal_handler = MagicMock()
        mock_bots_interactor.register_bots.return_value = mock_loop
        mock_bots_interactor.tasks = [asyncio.create_task(failing_task())]
        
        with pytest.raises(Exception) as exc_info:
            await main()
        assert "Task failed" in str(exc_info.value)

def test_setup_logger(tmp_path):
    """Test logger setup."""
    # Change to temporary directory
    os.chdir(tmp_path)
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]: # Copy the list to avoid modification during iteration
        root_logger.removeHandler(handler)
    
    # Set up logger
    setup_logger()
    
    # Verify logger configuration
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 2  # Console and file handler
    
    # Verify log file was created
    assert os.path.exists("buzzing.log")
    
    # Verify handler types
    handlers = root_logger.handlers
    assert any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in handlers)
    assert any(isinstance(h, logging.FileHandler) for h in handlers)
