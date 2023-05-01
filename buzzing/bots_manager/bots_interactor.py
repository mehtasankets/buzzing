from buzzing.dao.bots_config_dao import BotsConfigDao
from buzzing.bots_manager.bot_interactor import BotInteractor

class BotsInteractor():
    def __init__(self, db_connection):
        self.bots_config_dao = BotsConfigDao(db_connection)
        self.bots_config = self.bots_config_dao.fetch_all()

    def register_bots(self):
        for config in self.bots_config:
            BotInteractor(config)
