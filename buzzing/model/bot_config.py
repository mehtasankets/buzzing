from dataclasses import dataclass
from buzzing.bots.bot_interface import BotInterface

@dataclass(frozen=True)
class BotConfig():
    id: int
    name: str
    description: str
    token: str
    password: str
    bot: BotInterface
    metadata: dict
    is_active: bool
