from dataclasses import dataclass
from buzzing.bots.bot_interface import BotInterface

@dataclass(frozen=True)
class Subscription():
    user_id: int
    username: str
    bot_id: int
    is_active: bool
