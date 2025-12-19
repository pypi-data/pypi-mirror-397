import random
from AioSpider.tools import utility_tools


class BaseProxy:
    
    def __init__(
            self, ip: str, port: int, protocol: str = "http", username: str = None, password: str = None, **kwargs
    ):
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __str__(self):
        if self.username and self.password:
            return f'{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}'
        return f'{self.protocol}://{self.ip}:{self.port}'
    
    __repr__ = __str__


class Proxy(BaseProxy):
    """普通代理"""

    def __init__(self, weight: float = None, **kwargs):
        self.weight = weight
        super(Proxy, self).__init__(**kwargs)


class TurnelProxy(BaseProxy):
    """隧道代理"""
    pass
