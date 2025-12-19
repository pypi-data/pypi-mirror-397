__all__ = [
    'AsyncRdisAPI', 'SyncRdisAPI', 'RedisLock', 'Connector'
]

from .redis import AsyncRdisAPI, SyncRdisAPI, RedisLock


class Connector:

    def __init__(self):
        self._connector = dict()

    def __getitem__(self, name):
        return self._connector[name]

    def __setitem__(self, name, connect):
        setattr(self, name, connect)
        self._connector[name] = connect

    def __contains__(self, item):
        return item in self._connector

    def __str__(self):
        return f'Connector({self._connector})'

    __repr__ = __str__
