from collections import defaultdict

from AioSpider import logger
from AioSpider.http import HttpRequest

from .abc import HttpRequestQueue

__all__ = ['FailedRequestQueue']


class FailedRequestQueue(HttpRequestQueue):

    def __init__(self, max_retry_times):
        self.name = 'failure'
        self.failure_requests = set()
        self.max_retry_times = max_retry_times
        self.failure_counts = defaultdict(int)

    async def add_request(self, request: HttpRequest) -> HttpRequest:
        """将请求添加到失败队列"""
        if self.failure_counts[request.hash] >= self.max_retry_times:
            logger.level4(msg=f'请求失败次数超限，自动丢弃：{request}')
            return None
        else:
            logger.level4(msg=f'请求异常，系统将该请求添加到 failure 队列 {request}')
            self.failure_requests.add(request)
            self.failure_counts[request.hash] += 1
        return request

    async def delete_request(self, request: HttpRequest):
        """从失败队列中移除请求"""
        self.failure_requests.discard(request)
        if request.hash in self.failure_counts:
            del self.failure_counts[request.hash]
        logger.level4(msg=f'从 failure 队列中移除请求 {request}')

    async def fetch_requests(self, count):
        """从失败队列中获取指定数量的请求"""
        count = min(count, len(self.failure_requests))
        for _ in range(count):
            if not self.failure_requests:
                break
            yield self.failure_requests.pop()

    async def contains_request(self, request: HttpRequest):
        return  request in  self.failure_requests

    def get_queue_size(self):
        return len(self.failure_requests)

    def is_empty(self) -> bool:
        return self.get_queue_size() == 0

    def get_failure_times(self, request: HttpRequest):
        return self.failure_counts[request.hash]

    async def close(self):
        self.failure_requests.clear()
        self.failure_counts.clear()
