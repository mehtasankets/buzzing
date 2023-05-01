DROP TABLE IF EXISTS bots_config;

CREATE TABLE IF NOT EXISTS bots_config(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT,
    entry_module TEXT,
    entry_class TEXT,
    metadata TEXT,
    is_active BOOLEAN
);

INSERT INTO bots_config (token, entry_module, entry_class, metadata, is_active) values ('<TOKEN>', 'buzzing.bots.test_bot', 'TestBot', null, 1);