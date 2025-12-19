from collections import deque

from AioSpider.tools import utility_tools
from AioSpider.http import HttpRequest


class Queue(deque):
    
    async def put(self, value):
        if isinstance(value, list):
            self.extend(value)
        else:
            self.append(value)
    
    async def get(self):
        return self.popleft()
    
    async def empty(self):
        return len(self) == 0
    
    
class RedisQueue:

    redis_buffer_key = 'buffer'
    
    def __init__(self, conn, redis_spider_key):
        self.conn = conn
        self.redis_spider_key = redis_spider_key
        self.count = 0

    async def put(self, requests):

        if requests and not isinstance(requests, list):
            requests = []

        if not requests:
            return 

        self.count += await self.conn.set.sadd(
            f'{self.redis_spider_key}:{self.redis_buffer_key}',
            *[utility_tools.dump_json(request.to_dict()) for request in requests]
        )
    
    async def get(self):
        req = await self.conn.set.spop(f'{self.redis_spider_key}:{self.redis_buffer_key}')
        if req:
            self.count -= 1
            return HttpRequest.from_dict(utility_tools.load_json(req))
        return None

    async def empty(self):
        return await self.conn.set.scard(f'{self.redis_spider_key}:{self.redis_buffer_key}') == 0
