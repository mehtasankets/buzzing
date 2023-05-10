from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler
from buzzing.model.subscription import Subscription
import logging

HELP_STR = """
Supported commands:
    /help : To see this text
    /fetchnow : To fetch data on an ad-hoc basis
"""

PASSWORD = 0
LOG = logging.getLogger(__name__)

class BotInteractor():
    def __init__(self, config, subscriptions, bots_config_dao):
        self.config = config
        self.subscriptions = subscriptions
        self.bots_config_dao = bots_config_dao
        self.application = Application.builder().token(config.token).build()

        startHandler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.password)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        self.application.add_handler(startHandler)

        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("fetchnow", self.fetch_now))
        self.application.add_handler(CommandHandler("stop", self.stop))
        self.application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LOG.info(f'Start received from: {update.effective_chat}')
        await update.message.reply_html( # type: ignore
            f"Welcome <i>{update.effective_chat.first_name}</i> to <b>'{self.config.name}'</b> bot!\n" #type: ignore
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
        await update.message.reply_text( # type: ignore
            self.config.bot.fetch_now()
        )

    async def fetch(self):
        data = self.config.bot.fetch()
        for s in self.subscriptions:
            await self.application.bot.send_message(s.userId, data)
