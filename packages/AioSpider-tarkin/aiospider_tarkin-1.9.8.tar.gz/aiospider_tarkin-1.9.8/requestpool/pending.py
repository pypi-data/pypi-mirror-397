import time
from typing import Set, Tuple, Optional

from AioSpider import logger
from AioSpider.http import HttpRequest

from .abc import HttpRequestQueue

__all__ = ['PendingRequestQueue']


class PendingRequestQueue(HttpRequestQueue):

    def __init__(self):
        self.name = 'pending'
        self.pending: Set[Tuple[HttpRequest, float]] = set()

    async def add_request(self, request: HttpRequest) -> HttpRequest:
        """将请求添加到队列"""
        self.pending.add((request, time.time()))
        logger.level2(msg=f'1个请求添加到 pending 队列: \n{request}')
        return request

    async def fetch_requests(self, count: int = None) -> Optional[HttpRequest]:
        """从url池中取url"""
        if self.pending:
            return self.pending.pop()[0]
        return None

    async def contains_request(self, request: HttpRequest) -> bool:
        """判断请求是否存在"""
        return any(request == req for req, _ in self.pending)

    async def delete_request(self, request: HttpRequest) -> None:
        """把request移出队列"""
        self.pending = {(req, timestamp) for req, timestamp in self.pending if req != request}
        logger.level2(msg=f'1个请求从 pending 队列中删除: \n{request}')

    def get_queue_size(self) -> int:
        return len(self.pending)

    def is_empty(self) -> bool:
        return self.get_queue_size() == 0

    async def close(self) -> None:
        self.pending.clear()
        logger.level2(msg='pending 队列已关闭')
