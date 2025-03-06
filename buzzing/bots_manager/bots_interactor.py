from sqlite3 import Connection
from buzzing.dao.bots_config_dao import BotsConfigDao
from buzzing.bots_manager.bot_interactor import BotInteractor
from buzzing.model.bot_config import BotConfig
from buzzing.model.subscription import Subscription
import asyncio
import logging
from typing import List, Optional

LOG = logging.getLogger(__name__)

class BotsInteractor:
    """Manages multiple Telegram bots and their interactions.
    
    This class is responsible for initializing, managing, and gracefully shutting down
    multiple Telegram bots. It handles bot registration, task management, and ensures
    proper cleanup of resources.
    """

    def __init__(self, db_connection: Connection, task_timeout: float = 1.0):
        """Initialize the BotsInteractor.

        Args:
            db_connection: SQLite database connection for bot configurations
            task_timeout: Timeout in seconds to wait for each bot task to start
        """
        self.bots_config_dao = BotsConfigDao(db_connection)
        self.bots_config: List[BotConfig] = self.bots_config_dao.fetch_all_bots_configs()
        self.subscriptions: List[Subscription] = self.bots_config_dao.fetch_all_subscriptions()
        self.bot_interactors: List[BotInteractor] = []
        self.tasks: List[asyncio.Task] = []
        self.task_timeout = task_timeout

    async def register_bots(self) -> asyncio.AbstractEventLoop:
        """Register and initialize all bots asynchronously.

        Returns:
            The event loop managing the bot tasks

        Raises:
            Exception: If bot initialization fails
        """
        try:
            loop = asyncio.get_running_loop()
            for config in self.bots_config:
                bot_subscriptions = [s for s in self.subscriptions if s.bot_id == config.id]
                bot_interactor = BotInteractor(config, bot_subscriptions, self.bots_config_dao)
                self.bot_interactors.append(bot_interactor)
                
                # Create and track the task
                task = loop.create_task(
                    bot_interactor.initiate(), 
                    name=f"bot_{config.name}"
                )
                self.tasks.append(task)
                LOG.info(f'Created task for bot: {config.name}')
                
                # Wait for task to start or fail
                done, pending = await asyncio.wait(
                    [task], 
                    timeout=self.task_timeout,
                    return_when=asyncio.FIRST_EXCEPTION
                )
                
                # If task completed (probably with error), get the result to propagate exception
                if done:
                    await task
                elif pending:
                    LOG.info(f'Bot {config.name} started successfully')
            
            return loop
        except Exception as e:
            LOG.error(f"Error registering bots: {e}")
            await self.stop_bots()
            raise

    async def stop_bots(self) -> None:
        """Stop all bots gracefully."""
        LOG.info('Stopping all bots...')
        try:
            # First cancel all tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for all tasks to complete their cleanup
            await asyncio.gather(
                *[task for task in self.tasks if not task.done()],
                return_exceptions=True
            )
            
            # Now stop the bots (they will handle their own cleanup)
            await asyncio.gather(
                *[bot.stop_polling() for bot in self.bot_interactors],
                return_exceptions=True
            )
            
            self.tasks.clear()
            LOG.info('All bots stopped successfully')
        except Exception as e:
            LOG.error(f'Error during bot shutdown: {e}')
            raise