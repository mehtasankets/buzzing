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
            is_active BOOLEAN
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
