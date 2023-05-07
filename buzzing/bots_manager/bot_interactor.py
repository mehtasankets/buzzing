from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

HELP_STR = """
Supported commands:
    /help : To see this text
    /fetchnow : To fetch data on an ad-hoc basis
"""

PASSWORD = 0

class BotInteractor():
    def __init__(self, config):
        self.config = config
        print(self.config)
        self.application = Application.builder().token(config.token).build()
        print(self.application)

        startHandler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.password)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        self.application.add_handler(startHandler)

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("fetchnow", self.fetch_now))
        self.application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("Start received from: ")
        print(update.effective_chat)
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
        if(update.message and update.message.text == 'magic'):
            # TODO: Register user here
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

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
         await update.message.reply_text(HELP_STR)  # type: ignore

    async def fetch_now(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text( # type: ignore
            self.config.bot.fetch_now()
        )

    async def fetch(self):
        # TODO: Loop through users
        await self.application.bot.send_message(123, self.config.bot.fetch())
