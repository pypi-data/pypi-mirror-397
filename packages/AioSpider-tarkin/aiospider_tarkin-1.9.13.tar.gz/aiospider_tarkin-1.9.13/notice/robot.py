from abc import ABC, abstractmethod
from typing import List, Optional


class GroupRobot(ABC):
    """
    群机器人基类
    """

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.max_retry = 3

    @abstractmethod
    async def send_request(self, data: dict):
        pass

    @abstractmethod
    async def send_text(
            self, 
            content: str,
            at_mobiles: Optional[List[str]] = None,
            at_users: Optional[List[str]] = None,
            at_all: bool = False
    ):
        pass
