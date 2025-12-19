import time
import pickle
from pathlib import Path
from abc import abstractmethod

from AioSpider.tools import find_max, string_to_number
from AioSpider.exceptions import SettingsConfigException
from AioSpider.objects import BackendEngine, RequestStatus
from AioSpider.filter import BloomFilter
from AioSpider.http import HttpRequest

from .abc import HttpRequestQueue

__all__ = ['create_done_queue_factory']


class HttpRequestDatabase(HttpRequestQueue):
    
    def __init__(self):
        self.success_request_count = 0
        self.failed_request_count = 0
        self.success_request_hashes = set()
        self.failed_request_hashes = set()

    @abstractmethod
    async def load_requests(self, path: Path = None, status='success'):
        pass

    @abstractmethod
    async def dump_requests(self, path: Path, expire: int, strict=True):
        pass


class QueueRequestDatabase(HttpRequestDatabase):

    def __init__(self):
        super().__init__()
        self._filter = None
        self.filter_max_count = 10000
        self.filter_index = 0

    @property
    def filter(self):
        if self._filter is None:
            self._filter = [BloomFilter(capacity=self.filter_max_count)]
        if self.success_request_count // self.filter_max_count != self.filter_index:
            self._filter.append(BloomFilter(capacity=self.filter_max_count))
            self.filter_index += 1
        return self._filter[self.filter_index]
    
    async def fetch_requests(self, count):
        return [self.success_request_hashes.pop() for _ in range(count)]
    
    async def add_request(self, request: HttpRequest) -> HttpRequest:
        if request.status == RequestStatus.success:
            self.success_request_hashes.add(request.hash)
            self.filter.add(request.hash)
            self.success_request_count += 1
        elif request.status == RequestStatus.failed:
            self.failed_request_hashes.add(request.hash)
            self.failed_request_count += 1
        return request
    
    async def contains_request(self, request: HttpRequest):
        return request.hash in self.filter or request.hash in self.failed_request_hashes

    async def get_queue_size(self):
        return self.success_request_count + self.failed_request_count

    async def is_empty(self):
        return self.success_request_count == 0 and self.failed_request_count == 0

    async def load_requests(self, path: Path = None, status='success'):
        if not path or not path.exists():
            return False

        file_list = path.iterdir()
        expire_list = [string_to_number(i.stem.split('_')[-1], target_type=int, force_convert=True) for i in file_list]
        expire = find_max(expire_list)

        if expire < time.time():
            return

        file_path = path / f'{expire}.aio'
        if not file_path.exists():
            return

        with file_path.open('rb') as f:
            txt = f.read().decode()

        for request in txt.split('\n'):
            self.success_request_hashes.add(request)

    async def dump_requests(self, path: Path, expire: int, strict=True):
        if strict and len(self.success_request_hashes) < self.filter_max_count:
            return False

        file_path = path / f'{expire}.aio'
        txt = '\n'.join(self.success_request_hashes)
        await self.clear_success()

        with open(file_path, 'ab') as f:
            f.write(txt.encode())

        return True

    async def close(self):
        self.success_request_hashes.clear()
        self.failed_request_hashes.clear()
        self.success_request_count = 0
        self.failed_request_count = 0
        self._filter = None


class RedisRequestDatabase(HttpRequestDatabase):

    def __init__(self, spider, connector):
        super().__init__()
        self.success_key = f'{spider.name}:success'
        self.failure_key = f'{spider.name}:failure'
        self.conn = connector['redis']['DEFAULT']

    async def fetch_requests(self, count):
        return await self.conn.set.spop(self.success_key, count)

    async def add_request(self, request: HttpRequest) -> HttpRequest:
        if request.status == RequestStatus.success:
            await self.conn.set.sadd(self.success_key, request.hash)
            self.success_request_hashes.add(request.hash)
            self.success_request_count += 1
        elif request.status == RequestStatus.failed:
            await self.conn.set.sadd(self.failure_key, request.hash)
            self.failed_request_hashes.add(request.hash)
            self.failed_request_count += 1
        return request

    async def contains_request(self, request: HttpRequest):
        if request.hash in self.success_request_hashes or request.hash in self.failed_request_hashes:
            return True
        return await self.conn.set.sismember(self.success_key, request.hash) or \
               await self.conn.set.sismember(self.failure_key, request.hash)

    async def get_queue_size(self):
        return self.success_request_count + self.failed_request_count
    
    async def is_empty(self):
        return self.success_request_count == 0 and self.failed_request_count == 0

    async def load_requests(self, path: Path = None, status='success'):
        if not path or not path.exists():
            return False

        file_list = path.iterdir()
        expire_list = [string_to_number(i.stem.split('_')[-1], target_type=int, force_convert=True) for i in file_list]
        expire = find_max(expire_list)

        if expire < time.time():
            return

        file_path = path / f'request_{expire}.pkl'
        try:
            with file_path.open('rb') as f:
                txt = pickle.load(f)
        except Exception:
            return

        requests = [request for request in txt.split() if status in request]
        await self.conn.order_set.insert_many(status, requests)

    async def dump_requests(self, path: Path, expire: int, strict=True):
        if not path:
            return False

        request_list = []
        async for i in self.conn.zscan_iter(self.success_key):
            request_list.append(f'success_{i[0]}')
        async for i in self.conn.zscan_iter(self.failure_key):
            request_list.append(f'failure_{i[0]}')

        expire = int(time.time()) + expire
        file_path = path / f'request_{expire}.pkl'
        txt = '\n'.join(request_list)

        with file_path.open('wb') as f:
            pickle.dump(txt, f)

        await self.conn.order_set.delete(self.success_key)
        await self.conn.order_set.delete(self.failure_key)

        return True
    
    async def close(self):
        await self.conn.order_set.delete(self.success_key)
        await self.conn.order_set.delete(self.failure_key)
        self.success_request_count = 0
        self.success_request_hashes.clear()
        self.failed_request_count = 0
        self.failed_request_hashes.clear()


def create_done_queue_factory(backend, spider, connector):
    if backend == BackendEngine.queue:
        return QueueRequestDatabase()
    elif backend == BackendEngine.redis:
        return RedisRequestDatabase(spider, connector)  
    else:
        raise SettingsConfigException('无效的后端引擎类型')
