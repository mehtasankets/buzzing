DROP TABLE IF EXISTS bots_config;

CREATE TABLE IF NOT EXISTS bots_config(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    token TEXT,
    password TEXT,
    entry_module TEXT,
    entry_class TEXT,
    metadata TEXT,
    is_active BOOLEAN
);

INSERT INTO bots_config (name, description, token, password, entry_module, entry_class, metadata, is_active) 
values ('testbot1', 'Test bot for experimentations', '<token>', 'test123', 'buzzing.bots.test_bot', 'TestBot', null, 1);