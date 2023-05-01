from telegram.ext import Application, CommandHandler

class BotInteractor():
    def __init__(self, config):
        self.config = config
        print(self.config)
        self.application = Application.builder().token(config.token).build()
        print(self.application)
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("fetchnow", self.fetch_now))
        self.application.run_polling()

    def start(self):
        pass

    def help(self):
        pass

    def fetch_now(self):
        pass

    def fetch(self):
        pass
