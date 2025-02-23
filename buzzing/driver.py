import logging
import os
import sqlite3
import signal
import asyncio
from pathlib import Path
from sqlite3 import Connection
from typing import NoReturn
from buzzing.bots_manager.bots_interactor import BotsInteractor

LOG = logging.getLogger(__name__)

async def main() -> NoReturn:
    """Main entry point for the Buzzing application.

    This function:
    1. Sets up logging
    2. Initializes database connection
    3. Starts bot manager
    4. Handles graceful shutdown

    Raises:
        Exception: If there's an unrecoverable error during execution
    """
    setup_logger()
    LOG.info("Welcome to Buzzing!")

    # Get database path from environment or use default
    db_file_path = os.path.abspath(os.environ.get('BUZZING_DB_PATH', 'buzzing.db'))
    LOG.info(f"Using database at: {db_file_path}")

    try:
        # Initialize database connection
        connection = sqlite3.connect(
            db_file_path, 
            check_same_thread=False,  # Required for async operation
            isolation_level=None  # Enable autocommit mode
        )

        try:
            # Initialize and start bot manager
            bots_interactor = BotsInteractor(connection)
            loop = await bots_interactor.register_bots()

            # Set up signal handlers for graceful shutdown
            def signal_handler() -> None:
                """Handle shutdown signals by stopping all bots."""
                LOG.info("Received shutdown signal...")
                asyncio.create_task(bots_interactor.stop_bots())

            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, signal_handler)

            # Wait for all bot tasks to complete
            try:
                await asyncio.gather(*bots_interactor.tasks)
            except asyncio.CancelledError:
                LOG.info("Tasks cancelled, shutting down...")
            except Exception as e:
                LOG.error(f"Error in bot tasks: {e}")
                raise

        except Exception as e:
            LOG.error(f"Error in bot manager: {e}")
            raise
        finally:
            connection.close()
            LOG.info("Database connection closed")

    except Exception as e:
        LOG.error(f"Fatal error in main: {e}")
        raise
    finally:
        LOG.info("Bye bye!")

def setup_logger() -> None:
    """Configure application logging.

    Sets up logging to both console and file with appropriate formatting.
    Log file is created in the current directory as 'buzzing.log'.
    """
    try:
        # Create log formatter
        log_formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-13.13s] [%(levelname)-5.5s] %(name)s: %(message)s")

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

        # Add file handler
        log_file = Path("buzzing.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

        LOG.debug(f"Logging configured. Log file: {log_file.absolute()}")
    except Exception as e:
        print(f"Failed to configure logging: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
