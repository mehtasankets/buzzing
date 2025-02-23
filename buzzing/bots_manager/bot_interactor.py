from telegram import Update
from telegram.ext import (Application, CommandHandler, ContextTypes, 
                         ConversationHandler, filters, MessageHandler)
from buzzing.model.subscription import Subscription
from buzzing.model.bot_config import BotConfig
from buzzing.dao.bots_config_dao import BotsConfigDao
import logging
import asyncio
from typing import List, Optional, Dict, Any, cast

HELP_STR = """
Supported commands:
    /help : To see this text
    /fetchnow : To fetch data on an ad-hoc basis
"""

PASSWORD = 0
LOG = logging.getLogger(__name__)

class BotInteractor:
    """Handles interactions for a single Telegram bot.
    
    This class manages the lifecycle and command handling for a single bot instance,
    including user authentication, command processing, and graceful shutdown.
    """

    def __init__(self, config: BotConfig, subscriptions: List[Subscription], 
                 bots_config_dao: BotsConfigDao) -> None:
        """Initialize the bot interactor.

        Args:
            config: Bot configuration
            subscriptions: List of user subscriptions for this bot
            bots_config_dao: DAO for managing bot configurations
        """
        self.config = config
        self.subscriptions = subscriptions
        self.bots_config_dao = bots_config_dao
        self.application = Application.builder().token(config.token).build()
        
        # Initialize bot state
        self.stop_bot = False
        
        # Set up conversation handler for authentication
        self.start_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.password)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

    async def initiate(self) -> None:
        """Start the bot and begin polling for updates.

        This method runs indefinitely until stop_bot is set to True.
        """
        LOG.info(f'Initiating {self.config.description} bot!')
        try:
            async with self.application:
                # Register all command handlers
                self.application.add_handler(self.start_handler)
                self.application.add_handler(CommandHandler("help", self.help))
                self.application.add_handler(CommandHandler("fetchnow", self.fetch_now))
                self.application.add_handler(CommandHandler("stop", self.stop))
                
                # First, delete any existing webhook to ensure clean start
                await self.application.bot.delete_webhook(drop_pending_updates=True)
                
                # Start the application and polling
                await self.application.initialize()
                await self.application.start()
                await self.application.updater.start_polling()
                
                LOG.info(f'Bot {self.config.name} is now polling for updates!')
                
                # Use an event for cleaner shutdown
                stop_event = asyncio.Event()
                
                async def check_stop():
                    while not self.stop_bot:
                        try:
                            await asyncio.sleep(1)  # Check stop flag every second
                        except asyncio.CancelledError:
                            LOG.info(f'Bot {self.config.name} task cancelled, cleaning up...')
                            await self.stop_polling()
                            raise  # Re-raise to properly handle task cancellation
                    stop_event.set()
                
                # Create task for stop checking
                stop_task = asyncio.create_task(check_stop())
                
                try:
                    await stop_event.wait()
                finally:
                    stop_task.cancel()
                    try:
                        await stop_task
                    except asyncio.CancelledError:
                        pass
                    
                    # Graceful shutdown
                    await self.stop_polling()
        except Exception as e:
            LOG.error(f'Error in bot {self.config.name}: {e}')
            raise

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the /start command and begin authentication.

        Args:
            update: The update containing the command
            context: The context for this update

        Returns:
            The next conversation state (PASSWORD)
        """
        chat = cast(Any, update.effective_chat)
        LOG.info(f'Start received from: {chat.id}')
        await update.message.reply_html(
            f"Welcome <i>{chat.first_name}</i> to <b>'{self.config.name}'</b> bot!\n"
            f"<i>{self.config.description}</i>\n\n"
            f"Kindly provide a magic password to register yourself.\n"
            f"<i>(Reach out to @mehtasankets if you don't know the password!)</i>\n\n"
            f"Enter Password: "
        )
        return PASSWORD

    async def password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        password = update.message.text  # type: ignore
        if(update.message and update.message.text == self.config.password):
            subscription = Subscription(update.effective_user.id, update.effective_user.username, self.config.id, True) # type: ignore
            self.bots_config_dao.subscribe(subscription)
            await update.message.reply_text(
                "Great! Welcome to the bot! You'll start receiving information regularly!"
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text( # type: ignore
                "Nahh! Try again!"
            )
            return PASSWORD

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text( # type: ignore
            "Bye, Bye!"
        )
        return ConversationHandler.END

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LOG.info(f'Stop command received from{update.effective_chat}')
        subscription = Subscription(update.effective_user.id, update.effective_user.username, self.config.id, False) # type: ignore
        self.bots_config_dao.unsubscribe(subscription)
        await update.message.reply_html( # type: ignore
            f"Hey <i>{update.effective_chat.first_name}</i>,\n" #type: ignore
            f"It's sad to see you go. Hope you come back again later!\n"
        )
        return PASSWORD

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
         await update.message.reply_text(HELP_STR)  # type: ignore

    async def fetch_now(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LOG.info(f'Fetch now command received from {update.effective_chat}')
        
        # Check if user is subscribed
        if not update.effective_user or not any(s.user_id == update.effective_user.id for s in self.subscriptions):
            await update.message.reply_text(
                "You need to /start and authenticate first!"
            )
            return
        
        try:
            data = await self.config.bot.fetch_now()
            LOG.info(f'Fetched data: {data}')
            await update.message.reply_text(data)
        except Exception as e:
            LOG.error(f'Error in fetch_now: {e}')
            await update.message.reply_text(
                "Sorry, something went wrong while fetching data."
            )

    async def fetch(self):
        data = await self.config.bot.fetch()
        for s in self.subscriptions:
            await self.application.bot.send_message(s.user_id, data)

    async def stop_polling(self):
        """Stop the bot polling gracefully."""
        try:
            LOG.info(f'Stopping bot: {self.config.name}')
            self.stop_bot = True
            
            try:
                # First stop polling if updater exists and is running
                if hasattr(self.application, 'updater') and self.application.updater and self.application.updater.running:
                    await self.application.updater.stop()
                
                # Then stop and shutdown the application if it's running
                if hasattr(self.application, 'running') and self.application.running:
                    await self.application.stop()
                    if hasattr(self.application, 'shutdown'):
                        await self.application.shutdown()
                
                LOG.info(f'Bot stopped: {self.config.name}')
            except RuntimeError as e:
                # Handle case where components are already stopped
                if 'not running' not in str(e).lower():
                    raise
                LOG.debug(f'Component already stopped for bot {self.config.name}: {str(e)}')
                
        except Exception as e:
            LOG.error(f'Error stopping bot {self.config.name}: {str(e)}')
