from buzzing.dao.bots_config_dao import BotsConfigDao
from buzzing.bots_manager.bot_interactor import BotInteractor

class BotsInteractor():
    def __init__(self, db_connection):
        self.bots_config_dao = BotsConfigDao(db_connection)
        self.bots_config = self.bots_config_dao.fetch_all_bots_configs()
        self.subsciptions = self.bots_config_dao.fetch_all_subscriptions()

    def register_bots(self):
        for config in self.bots_config:
            bot_subscriptions =  [ s for s in self.subsciptions if s.bot_id == config.id ]
            BotInteractor(config, bot_subscriptions, self.bots_config_dao)
