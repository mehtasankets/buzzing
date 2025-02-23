from dataclasses import dataclass

@dataclass(frozen=True)
class Subscription:
    """User subscription to a Telegram bot.
    
    Represents a user's subscription status to a specific bot.
    
    Attributes:
        user_id: Telegram user ID
        username: Telegram username
        bot_id: ID of the bot being subscribed to
        is_active: Whether the subscription is currently active
    """
    user_id: int
    username: str
    bot_id: int
    is_active: bool
