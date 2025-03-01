# Buzzing 🔔

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-package%20manager-blue)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mehtasankets/buzzing/actions/workflows/test.yml/badge.svg)](https://github.com/mehtasankets/buzzing/actions)
[![codecov](https://codecov.io/gh/mehtasankets/buzzing/branch/main/graph/badge.svg)](https://codecov.io/gh/mehtasankets/buzzing)

Buzzing is a Telegram notification system that helps you manage and send important notifications through multiple bots. Built with asyncio for efficient concurrent operations.

## 🌟 Features

- Multiple bot management
- Asynchronous message handling
- SQLite persistence
- Graceful shutdown handling
- Configurable notification rules

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Linux/Unix environment

## 🚀 Quick Start

1. **System Dependencies**
```bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv
```

2. **Install Poetry**
```bash
# Using apt (recommended)
sudo apt install -y python3-poetry

# OR using pipx
sudo apt install -y pipx && pipx ensurepath && pipx install poetry
```

3. **Install Project Dependencies**
```bash
poetry install
```

4. **Start the Application**
```bash
poetry run python -m buzzing.driver
```

## 💻 Development

### Environment Setup

1. **Clone the Repository**
```bash
git clone https://github.com/mehtasankets/buzzing.git
cd buzzing
```

2. **Configure VSCode**
- Install recommended extensions
- Set Python interpreter:
  ```bash
  poetry env info --path  # Copy this path
  # In VSCode: Ctrl+Shift+P > Python: Select Interpreter > Enter path
  ```

### Running Tests

**Via Command Line:**
```bash
poetry run pytest
```

**Via VSCode:**
- Open Testing sidebar (flask icon)
- Click play button to run all tests
- Individual tests can be run with their respective play buttons

### Application Control

**Start:**
```bash
poetry run python -m buzzing.driver
```

**Stop:**
- Press `Ctrl+C` in the terminal, or
- Run: `pkill -SIGINT -f "python -m buzzing.driver"`

### Logs

Application logs are written to `buzzing.log`. Monitor in real-time:
```bash
tail -f buzzing.log
```

## 🔧 Configuration

The application uses SQLite for configuration storage. The database schema is defined in `etc/db_config/v0.sql`.

### Bot Configuration

Bots are configured in the `bots_config` table:
```sql
CREATE TABLE bots_config(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,                -- Bot name
    description TEXT,         -- Bot description
    token TEXT,              -- Telegram bot token
    password TEXT,           -- Bot password
    entry_module TEXT,       -- Python module containing bot implementation
    entry_class TEXT,        -- Python class name for the bot
    metadata TEXT,           -- Additional JSON configuration
    is_active BOOLEAN        -- Bot active status
);
```

### User Subscriptions

User subscriptions are managed in the `subscription` table:
```sql
CREATE TABLE subscription(
    user_id INTEGER,         -- Telegram user ID
    username TEXT,           -- Telegram username
    bot_id INTEGER,          -- Reference to bots_config.id
    is_active BOOLEAN,       -- Subscription status
    PRIMARY KEY (user_id, bot_id)
);
```

The database is automatically initialized with test bots when you first run the application.

## 📝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the excellent Telegram API wrapper
