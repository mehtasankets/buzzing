import abc

class BotInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'fetch') and
                callable(subclass.fetch) and
                hasattr(subclass, 'fetch_now') and
                callable(subclass.fetch_now) or
                NotImplemented)

    @abc.abstractmethod
    def fetch(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_now(self):
        raise NotImplementedError
