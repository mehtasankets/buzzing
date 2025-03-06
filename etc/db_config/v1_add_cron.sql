-- Add cron column to bots_config table if it doesn't exist
PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

-- Create a temporary table with the desired schema
CREATE TABLE IF NOT EXISTS bots_config_new (
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
);

-- Copy data from the old table to the new one
INSERT OR IGNORE INTO bots_config_new 
SELECT id, name, description, token, password, entry_module, entry_class, metadata, is_active, NULL as cron
FROM bots_config;

-- Drop the old table and rename the new one
DROP TABLE IF EXISTS bots_config_old;
ALTER TABLE bots_config RENAME TO bots_config_old;
ALTER TABLE bots_config_new RENAME TO bots_config;

UPDATE bots_config SET cron = '*/1 * * * *' WHERE entry_module = 'buzzing.bots.test_bot';

-- Insert StockMarketBot configuration if it doesn't exist already
INSERT OR IGNORE INTO bots_config (
    name, 
    description, 
    token, 
    password, 
    entry_module, 
    entry_class, 
    metadata, 
    is_active, 
    cron
) SELECT
    'Stock Market Updates', 
    'Provides regular updates on Sensex and Nifty values', 
    '<YOUR_TELEGRAM_BOT_TOKEN>', 
    'stockmarket123', 
    'buzzing.bots.stock_market_bot', 
    'StockMarketBot', 
    '{}', 
    1, 
    '*/1 * * * *'  -- Run every 1 minute
WHERE NOT EXISTS (
    SELECT 1 FROM bots_config WHERE entry_module = 'buzzing.bots.stock_market_bot'
);

COMMIT;
PRAGMA foreign_keys=on;
