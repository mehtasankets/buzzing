from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

T = TypeVar('T', bound='BotInterface')

class BotInterface(ABC):
    """Abstract base class for Telegram bot implementations.
    
    This interface defines the required methods that all bot implementations
    must provide. It supports both scheduled and on-demand data fetching.
    """

    @classmethod
    def __subclasshook__(cls: Type[T], subclass: Type[Any]) -> bool:
        """Check if a class implements the required interface.

        Args:
            subclass: The class to check

        Returns:
            True if the class implements fetch and fetch_now methods
        """
        return (hasattr(subclass, 'fetch') and
                callable(subclass.fetch) and
                hasattr(subclass, 'fetch_now') and
                callable(subclass.fetch_now) or
                NotImplemented)

    @abstractmethod
    async def fetch(self) -> Any:
        """Fetch data on a scheduled basis.

        Returns:
            The fetched data in any format

        Raises:
            NotImplementedError: If the method is not implemented
        """
        raise NotImplementedError("Subclass must implement fetch()")

    @abstractmethod
    async def fetch_now(self) -> Any:
        """Fetch data immediately on demand.

        Returns:
            The fetched data in any format

        Raises:
            NotImplementedError: If the method is not implemented
        """
        raise NotImplementedError("Subclass must implement fetch_now()")
