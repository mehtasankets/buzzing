import json
from buzzing.model.bot_config import BotConfig
from buzzing.model.subscription import Subscription
from buzzing.util.class_loader import class_from_string

class BotsConfigDao():

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def fetch_all_bots_configs(self):
        cursor = self.db_connection.execute(
            """
                SELECT
                    id, name, description, token, password, entry_module, entry_class, metadata, is_active
                FROM bots_config
                WHERE is_active = 1
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

    def fetch_all_subscriptions(self):
        cursor = self.db_connection.execute(
            """
                SELECT
                    user_id, username, bot_id, is_active
                FROM subscription
                WHERE is_active = 'True'
            """)
        return [Subscription(c[0], c[1], c[2], bool(c[3])) for c in cursor]

    def subscribe(self, subscription):
        self.db_connection.execute(
            f"""
                INSERT INTO subscription(user_id, username, bot_id, is_active)
                VALUES({subscription.user_id}, '{subscription.username}', '{subscription.bot_id}', '{subscription.is_active}')
                ON CONFLICT(user_id, bot_id) DO UPDATE SET
                username = excluded.username,
                is_active = excluded.is_active
            """)
        self.db_connection.commit()

    def unsubscribe(self, subscription):
        self.db_connection.execute(
            f"""
                UPDATE subscription
                SET is_active = 'False'
                WHERE user_id = '{subscription.user_id}'
                    AND bot_id = '{subscription.bot_id}'
            """)
        self.db_connection.commit()
