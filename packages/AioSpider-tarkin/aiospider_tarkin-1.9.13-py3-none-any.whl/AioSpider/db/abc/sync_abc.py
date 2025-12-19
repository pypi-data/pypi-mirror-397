from abc import ABCMeta, abstractmethod

from AioSpider.signal import Signal
from AioSpider.constants import SignalType


class SyncABC(metaclass=ABCMeta):
    
    def __init__(self, *args, **kwargs):
        Signal().connect(SignalType.database_close, self.close)

    @abstractmethod
    def find(self):
        pass

    @abstractmethod
    def insert(self, table: str, items: dict):
        pass
    
    @abstractmethod
    async def update(self, table: str, items: dict):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def close(self):
        pass
