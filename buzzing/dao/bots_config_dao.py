import json
from buzzing.model.bot_config import BotConfig
from buzzing.util.class_loader import class_from_string

class BotsConfigDao():

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def fetch_all(self):
        cursor = self.db_connection.execute(
            """
                SELECT
                    id, name, description, token, password, entry_module, entry_class, metadata, is_active
                FROM bots_config
            """)
        bot_configs = []
        for c in cursor:
            bot_class = class_from_string(c[5], c[6])
            bot = bot_class()
            metadata = '{}' if c[7] is None else c[7]
            is_active = bool(int(c[8]))
            config = BotConfig(c[0], c[1], c[2], c[3], c[4], bot, json.loads(metadata), is_active)
            bot_configs.append(config)
        return bot_configs
