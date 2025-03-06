"""Tests for BotsConfigDao."""
import pytest
import sqlite3
from buzzing.dao.bots_config_dao import BotsConfigDao
from buzzing.model.subscription import Subscription

@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    
    # Create tables
    conn.execute('''
        CREATE TABLE bots_config(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            token TEXT,
            password TEXT,
            entry_module TEXT,
            entry_class TEXT,
            metadata TEXT,
            is_active BOOLEAN,
            cron TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE subscription(
            user_id INTEGER,
            username TEXT,
            bot_id INTEGER,
            is_active BOOLEAN,
            PRIMARY KEY (user_id, bot_id)
        )
    ''')
    
    # Insert test data
    conn.execute('''
        INSERT INTO bots_config (name, description, token, password, entry_module, entry_class, metadata, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test_bot', 'Test Bot', 'test_token', 'test_pass', 'buzzing.bots.test_bot', 'TestBot', '{}', 1))
    
    return conn

@pytest.fixture
def dao(db_connection):
    """Create a BotsConfigDao instance."""
    return BotsConfigDao(db_connection)

def test_fetch_all_bots_configs(dao):
    """Test fetching all bot configurations."""
    configs = dao.fetch_all_bots_configs()
    assert len(configs) == 1
    config = configs[0]
    assert config.name == 'test_bot'
    assert config.description == 'Test Bot'
    assert config.is_active is True

def test_fetch_all_subscriptions(dao, db_connection):
    """Test fetching all subscriptions."""
    # Insert test subscription
    db_connection.execute('''
        INSERT INTO subscription (user_id, username, bot_id, is_active)
        VALUES (?, ?, ?, ?)
    ''', (123456789, 'test_user', 1, 'True'))
    
    subscriptions = dao.fetch_all_subscriptions()
    assert len(subscriptions) == 1
    sub = subscriptions[0]
    assert sub.user_id == 123456789
    assert sub.username == 'test_user'
    assert sub.is_active is True

def test_subscribe_new_user(dao):
    """Test subscribing a new user."""
    subscription = Subscription(
        user_id=987654321,
        username='new_user',
        bot_id=1,
        is_active=True
    )
    dao.subscribe(subscription)
    
    subscriptions = dao.fetch_all_subscriptions()
    assert len(subscriptions) == 1
    assert subscriptions[0].user_id == 987654321

def test_unsubscribe_user(dao, db_connection):
    """Test unsubscribing a user."""
    # Insert test subscription
    db_connection.execute('''
        INSERT INTO subscription (user_id, username, bot_id, is_active)
        VALUES (?, ?, ?, ?)
    ''', (123456789, 'test_user', 1, 'True'))
    
    subscription = Subscription(
        user_id=123456789,
        username='test_user',
        bot_id=1,
        is_active=True
    )
    dao.unsubscribe(subscription)
    
    # Should not appear in active subscriptions
    subscriptions = dao.fetch_all_subscriptions()
    assert len(subscriptions) == 0

def test_sql_injection_prevention(dao):
    """Test that SQL injection is prevented."""
    malicious_subscription = Subscription(
        user_id=123456789,
        username="'; DROP TABLE subscription; --",
        bot_id=1,
        is_active=True
    )
    
    # This should not raise an error and should properly escape the malicious input
    dao.subscribe(malicious_subscription)
    
    # Table should still exist and we should be able to query it
    subscriptions = dao.fetch_all_subscriptions()
    assert len(subscriptions) == 1


def test_subscribe_update_existing(dao):
    """Test updating an existing subscription."""
    # Create initial subscription
    subscription1 = Subscription(
        user_id=111222333,
        username="original_name",
        bot_id=1,
        is_active=True
    )
    dao.subscribe(subscription1)
    
    # Update same user with new username
    subscription2 = Subscription(
        user_id=111222333,
        username="updated_name",
        bot_id=1,
        is_active=True
    )
    dao.subscribe(subscription2)
    
    # Should have only one subscription with updated username
    subscriptions = dao.fetch_all_subscriptions()
    matching = [s for s in subscriptions if s.user_id == 111222333]
    assert len(matching) == 1
    assert matching[0].username == "updated_name"


def test_fetch_all_bots_configs_with_invalid_class(dao, db_connection):
    """Test fetching bot configs with invalid module/class references."""
    # Insert a bot config with invalid module/class
    db_connection.execute('''
        INSERT INTO bots_config (name, description, token, password, entry_module, entry_class, metadata, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('invalid_bot', 'Invalid Bot', 'token', 'pass', 'invalid.module', 'InvalidClass', '{}', 1))
    
    # This should not raise an exception but log an error and skip the invalid config
    configs = dao.fetch_all_bots_configs()
    # Should only get the valid configs (1 from fixture)
    valid_configs = [c for c in configs if c.name == 'test_bot']
    assert len(valid_configs) == 1


def test_fetch_all_bots_configs_with_invalid_json(dao, db_connection):
    """Test fetching bot configs with invalid JSON in metadata."""
    # Insert a bot config with invalid JSON in metadata
    db_connection.execute('''
        INSERT INTO bots_config (name, description, token, password, entry_module, entry_class, metadata, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('json_error_bot', 'JSON Error Bot', 'token', 'pass', 'buzzing.bots.test_bot', 'TestBot', '{invalid json', 1))
    
    # This should not raise an exception but log an error and skip the invalid config
    configs = dao.fetch_all_bots_configs()
    # Should only get the valid configs (1 from fixture)
    valid_configs = [c for c in configs if c.name == 'test_bot']
    assert len(valid_configs) == 1


class MockErrorConnection:
    """A mock connection that raises errors for testing."""
    def __init__(self, error_type=sqlite3.OperationalError, error_msg="Mock database error"):
        self.error_type = error_type
        self.error_msg = error_msg
    
    def execute(self, *args, **kwargs):
        raise self.error_type(self.error_msg)
    
    def commit(self):
        raise self.error_type(self.error_msg)
    
    def rollback(self):
        # Allow rollback to succeed
        pass


def test_database_error_handling():
    """Test error handling for database operations."""
    # Create a DAO with a connection that will raise errors
    error_dao = BotsConfigDao(MockErrorConnection())
    
    # Test fetch_all_bots_configs error handling
    with pytest.raises(sqlite3.OperationalError):
        error_dao.fetch_all_bots_configs()
    
    # Test fetch_all_subscriptions error handling
    with pytest.raises(sqlite3.OperationalError):
        error_dao.fetch_all_subscriptions()
    
    # Test subscribe error handling
    subscription = Subscription(user_id=999, username="error_test", bot_id=1, is_active=True)
    with pytest.raises(sqlite3.OperationalError):
        error_dao.subscribe(subscription)
    
    # Test unsubscribe error handling
    with pytest.raises(sqlite3.OperationalError):
        error_dao.unsubscribe(subscription)
