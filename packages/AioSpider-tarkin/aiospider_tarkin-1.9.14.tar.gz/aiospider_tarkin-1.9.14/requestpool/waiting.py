from collections import defaultdict, deque
from typing import Dict, Deque
from heapq import heappush, heappop

from AioSpider import logger
from AioSpider.objects import BackendEngine
from AioSpider.http import HttpRequest
from AioSpider.tools import utility_tools

from .abc import HttpRequestQueue

__all__ = ['create_waiting_queue_factory']


class WaitingRequestQueue(HttpRequestQueue):

    def __init__(self, depth_priority: bool):
        self.name = 'waiting'
        self.waiting: Dict[str, Deque[HttpRequest]] = defaultdict(deque)
        self.depth_priority = depth_priority
        self.waiting_request_count = 0
        self.host_heap = []
        self.request_hash_counts: Dict[str, Dict[str, int]] = defaultdict(dict)

    async def add_request(self, request: HttpRequest) -> HttpRequest:
        host = request.url.domain
        
        if self.depth_priority:
            self.waiting[host].appendleft(request)  # 深度优先，使用后进先出
        else:
            self.waiting[host].append(request)      # 广度优先，使用先进先出
        
        self.waiting_request_count += 1
        self.request_hash_counts[host][request.hash] = self.request_hash_counts[host].get(request.hash, 0) + 1
        
        heappush(self.host_heap, (-len(self.waiting[host]), host))

        logger.level2(msg=f'1个请求添加到 waiting 队列\n{request}')
        return request

    async def fetch_requests(self, count: int):
        requests_obtained = 0

        while requests_obtained < count and self.waiting_request_count > 0:
            if not self.host_heap:
                break

            _, host = heappop(self.host_heap)
            
            while self.waiting[host] and requests_obtained < count:
                request = self.waiting[host].popleft()
                self._update_request_hashes(request)
                requests_obtained += 1
                self.waiting_request_count -= 1
                yield request

            if self.waiting[host]:
                heappush(self.host_heap, (-len(self.waiting[host]), host))
            else:
                del self.waiting[host]

    def _update_request_hashes(self, request: HttpRequest):
        host = request.url.domain
        if request.hash in self.request_hash_counts[host]:
            if self.request_hash_counts[host][request.hash] > 1:
                self.request_hash_counts[host][request.hash] -= 1
            else:
                del self.request_hash_counts[host][request.hash]

    async def contains_request(self, request: HttpRequest) -> bool:
        return request.hash in self.request_hash_counts.get(request.url.domain, {})

    async def get_queue_size(self) -> int:
        return self.waiting_request_count

    async def is_empty(self) -> bool:
        return self.waiting_request_count == 0
                
    async def close(self):
        self.waiting.clear()
        self.waiting_request_count = 0
        self.host_heap.clear()
        self.request_hash_counts.clear()


class RedisWaitingRequestQueueQueue(HttpRequestQueue):

    def __init__(self, connector, spider, depth_priority: bool):
        self.name = 'redis waiting'
        self.conn = connector['redis']['DEFAULT']
        self.spider = spider
        self.depth_priority = depth_priority
        self.redis_request_key = f'{self.spider.name}:waiting'

    async def add_request(self, request: HttpRequest) -> HttpRequest:
        await self.conn.order_set.zadd(
            self.redis_request_key,
            {utility_tools.dump_json(request.to_dict()): utility_tools.make_timestamp()}
        )
        return request

    async def fetch_requests(self, count: int):
        requests = await self.conn.order_set.zrange(self.redis_request_key, 0, count - 1)
        if requests:
            await self.conn.order_set.zrem(self.redis_request_key, *requests)
            for req in requests:
                yield HttpRequest.from_dict(utility_tools.load_json(req))

    async def contains_request(self, request: HttpRequest) -> bool:
        score = await self.conn.order_set.zscore(
            self.redis_request_key,
            utility_tools.dump_json(request.to_dict())
        )
        return score is not None

    async def get_queue_size(self) -> int:
        return await self.conn.order_set.zcard(self.redis_request_key)

    async def is_empty(self) -> bool:
        return await self.get_queue_size() == 0

    async def close(self):
        await self.conn.delete(self.redis_request_key)
        self.conn = None


def create_waiting_queue_factory(backend, connector, spider, depth_priority: bool):
    if backend == BackendEngine.queue:
        return WaitingRequestQueue(depth_priority)
    elif backend == BackendEngine.redis:
        return RedisWaitingRequestQueueQueue(connector, spider, depth_priority)
    else:
        raise ValueError(f"未知的队列类型: {backend}")
