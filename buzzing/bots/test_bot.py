from buzzing.bots.bot_interface import BotInterface

class TestBot(BotInterface):

    def fetch(self):
        print("test successful")

    def fetch_now(self):
        print("test successful for now")