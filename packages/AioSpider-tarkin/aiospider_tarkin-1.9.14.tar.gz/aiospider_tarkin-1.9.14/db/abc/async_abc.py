from abc import ABCMeta, abstractmethod

from AioSpider.signals import Signal
from AioSpider.constants import SignalType


class AsyncABC(metaclass=ABCMeta):

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.connect()
    
    def __init__(self, *args, **kwargs):
        Signal().connect(SignalType.database_close, self.close)

    @abstractmethod
    async def find(self, table: str, encoding=None):
        pass

    @abstractmethod
    async def insert(self, table: str, items: list, auto_update: bool = False):
        pass

    @abstractmethod
    async def delete(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def close(self):
        pass
