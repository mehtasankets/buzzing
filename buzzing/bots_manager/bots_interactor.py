from buzzing.dao.bots_config_dao import BotsConfigDao
from buzzing.bots_manager.bot_interactor import BotInteractor
import asyncio
import logging

LOG = logging.getLogger(__name__)

class BotsInteractor():
    def __init__(self, db_connection):
        self.bots_config_dao = BotsConfigDao(db_connection)
        self.bots_config = self.bots_config_dao.fetch_all_bots_configs()
        self.subsciptions = self.bots_config_dao.fetch_all_subscriptions()
        self.bot_interactors = []

    def register_bots(self):
        loop = None
        for config in self.bots_config:
            bot_subscriptions =  [ s for s in self.subsciptions if s.bot_id == config.id ]
            bot_interactor = BotInteractor(config, bot_subscriptions, self.bots_config_dao)
            loop = self.initiate_bot(bot_interactor, config)
            self.bot_interactors.append(bot_interactor)
        return loop

    def stop_bots(self):
        for bot_interactor in self.bot_interactors:
            bot_interactor.stop_polling()

    def initiate_bot(self, bot_interactor, config):
        loop = asyncio.get_event_loop()
        loop.create_task(bot_interactor.initiate(), name=config.name)
        LOG.info('Returning from initiate!')
        return loop