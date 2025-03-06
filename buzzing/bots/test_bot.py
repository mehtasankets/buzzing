from buzzing.bots.bot_interface import BotInterface

class TestBot(BotInterface):
    """A test implementation of BotInterface for development and testing.
    
    This bot simply returns static messages to verify the bot infrastructure
    is working correctly.
    """

    async def fetch(self) -> str:
        """Fetch test data on schedule.

        Returns:
            A test success message
        """
        return "test successful"

    async def fetch_now(self) -> str:
        """Fetch test data on demand.

        Returns:
            A test success message
        """
        return "test successful for now"