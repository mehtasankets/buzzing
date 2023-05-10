from buzzing.bots.bot_interface import BotInterface

class TestBot(BotInterface):

    def fetch(self):
        return "test successful"

    def fetch_now(self):
        return "test successful for now"