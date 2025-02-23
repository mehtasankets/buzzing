from dataclasses import dataclass
from typing import Dict, Any
from buzzing.bots.bot_interface import BotInterface

@dataclass(frozen=True)
class BotConfig:
    """Configuration for a Telegram bot.
    
    This class holds all necessary configuration for a single Telegram bot instance,
    including its credentials and runtime settings.
    
    Attributes:
        id: Unique identifier for the bot
        name: Display name of the bot
        description: Human-readable description of the bot's purpose
        token: Telegram API token for authentication
        password: Password for user registration
        bot: Instance of the bot implementation
        metadata: Additional configuration parameters
        is_active: Whether the bot is currently active
    """
    id: int
    name: str
    description: str
    token: str
    password: str
    bot: BotInterface
    metadata: Dict[str, Any]
    is_active: bool
