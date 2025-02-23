import json
import logging
from sqlite3 import Connection, Error as SQLiteError
from typing import List, Optional
from buzzing.model.bot_config import BotConfig
from buzzing.model.subscription import Subscription
from buzzing.util.class_loader import class_from_string

LOG = logging.getLogger(__name__)

class BotsConfigDao:
    """Data Access Object for bot configurations and subscriptions.
    
    Handles all database operations related to bot configurations and user subscriptions.
    Uses parameterized queries to prevent SQL injection.
    """

    def __init__(self, db_connection: Connection):
        """Initialize the DAO with a database connection.

        Args:
            db_connection: SQLite database connection
        """
        self.db_connection = db_connection

    def fetch_all_bots_configs(self) -> List[BotConfig]:
        """Fetch all active bot configurations.

        Returns:
            List of active bot configurations

        Raises:
            SQLiteError: If database operation fails
        """
        try:
            cursor = self.db_connection.execute(
                """
                SELECT
                    id, name, description, token, password, 
                    entry_module, entry_class, metadata, is_active
                FROM bots_config
                WHERE is_active = ?
                """, (1,))
            
            bot_configs = []
            for row in cursor:
                try:
                    bot_class = class_from_string(row[5], row[6])
                    bot = bot_class()
                    metadata = '{}' if row[7] is None else row[7]
                    is_active = bool(int(row[8]))
                    config = BotConfig(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        token=row[3],
                        password=row[4],
                        bot=bot,
                        metadata=json.loads(metadata),
                        is_active=is_active
                    )
                    bot_configs.append(config)
                except Exception as e:
                    LOG.error(f"Error creating bot config for {row[1]}: {e}")
            return bot_configs
        except SQLiteError as e:
            LOG.error(f"Database error in fetch_all_bots_configs: {e}")
            raise

    def fetch_all_subscriptions(self) -> List[Subscription]:
        """Fetch all active subscriptions.

        Returns:
            List of active subscriptions

        Raises:
            SQLiteError: If database operation fails
        """
        try:
            cursor = self.db_connection.execute(
                """
                SELECT
                    user_id, username, bot_id, is_active
                FROM subscription
                WHERE is_active = ?
                """, ('True',))
            return [Subscription(
                user_id=row[0],
                username=row[1],
                bot_id=row[2],
                is_active=bool(row[3])
            ) for row in cursor]
        except SQLiteError as e:
            LOG.error(f"Database error in fetch_all_subscriptions: {e}")
            raise

    def subscribe(self, subscription: Subscription) -> None:
        """Subscribe a user to a bot.

        Args:
            subscription: Subscription details

        Raises:
            SQLiteError: If database operation fails
        """
        try:
            self.db_connection.execute(
                """
                INSERT INTO subscription(user_id, username, bot_id, is_active)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(user_id, bot_id) DO UPDATE SET
                username = excluded.username,
                is_active = excluded.is_active
                """, (
                    subscription.user_id,
                    subscription.username,
                    subscription.bot_id,
                    str(subscription.is_active)
                ))
            self.db_connection.commit()
        except SQLiteError as e:
            LOG.error(f"Database error in subscribe: {e}")
            self.db_connection.rollback()
            raise

    def unsubscribe(self, subscription: Subscription) -> None:
        """Unsubscribe a user from a bot.

        Args:
            subscription: Subscription to deactivate

        Raises:
            SQLiteError: If database operation fails
        """
        try:
            self.db_connection.execute(
                """
                UPDATE subscription
                SET is_active = ?
                WHERE user_id = ? AND bot_id = ?
                """, (
                    'False',
                    subscription.user_id,
                    subscription.bot_id
                ))
            self.db_connection.commit()
        except SQLiteError as e:
            LOG.error(f"Database error in unsubscribe: {e}")
            self.db_connection.rollback()
            raise
