import asyncio
import time
from pathlib import Path
from typing import AsyncGenerator

from AioSpider import logger
from AioSpider.objects import EventType, BackendEngine, RequestStatus
from AioSpider.http import HttpRequest

from .done import create_done_queue_factory
from .pending import PendingRequestQueue
from .failure import FailedRequestQueue
from .waiting import create_waiting_queue_factory

__all__ = ['RequestPoolManager']


class QueueFactory:
    """请求队列工厂类"""

    @staticmethod
    def create(queue_type, *args, **kwargs):
        factories = {
            'waiting': create_waiting_queue_factory,
            'pending': PendingRequestQueue,
            'failure': FailedRequestQueue,
            'done': create_done_queue_factory
        }
        if queue_type not in factories:
            raise ValueError(f"未知队列类型: {queue_type}")
        return factories[queue_type](*args, **kwargs)


class RequestPoolManager:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.load_cache()

    def __init__(self, event_engine, spider, settings, connector, backend=BackendEngine.queue):
        self.event_engine = event_engine
        self.spider = spider
        self.settings = settings
        self._active = False
        self._request_queue = asyncio.Queue()
        self.waiting = QueueFactory.create(
            'waiting', backend, connector, spider, settings.SpiderRequestConfig.DepthPriority
        )
        self.pending = QueueFactory.create('pending')
        self.failure = QueueFactory.create('failure', settings.SpiderRequestConfig.MAX_FAILURE_RETRY_TIMES)
        self.done = QueueFactory.create('done', backend, spider, connector)
        self._last_percent = 0
        self._run_task = None
        event_engine.register(EventType.REQUEST_CLOSE, self.close)
        event_engine.register_timer(1, self.update_progress)

    def start(self):
        self._active = True
        self._run_task = asyncio.create_task(self._run())

    async def stop(self):
        self._active = False
        if self._run_task:
            self._run_task.cancel()
        logger.level3(msg=f'请求池已停止')

    async def _run(self):
        while self._active:
            try:
                request = await asyncio.wait_for(self._request_queue.get(), timeout=0.01)
                await self._process_request(request)
            except asyncio.TimeoutError:
                continue

    async def _process_request(self, request):
        if await self.pending.contains_request(request):
            await self.pending.delete_request(request)

        if request.status == RequestStatus.before:
            if await self.is_valid(request):
                await self.waiting.add_request(request)
        elif request.status == RequestStatus.success:
            await self.done.add_request(request)
        elif request.status == RequestStatus.failed:
            if not await self.failure.add_request(request):
                await self.done.add_request(request)

    async def put(self, request: HttpRequest):
        await self._request_queue.put(request)

    async def close(self):
        await self.stop()
        await self.save_cache()
        for queue in [self.waiting, self.pending, self.failure, self.done]:
            await queue.close()

    async def load_cache(self):
        cache_settings = self.settings.RequestFilterConfig
        if cache_settings.Enabled and cache_settings.LoadSuccess:
            cache_path = Path(cache_settings.CachePath) / self.spider.name
            await self.done.load_requests(path=cache_path)
        return self

    async def save_cache(self):
        cache_settings = self.settings.RequestFilterConfig

        if not cache_settings.Enabled:
            return

        expire = 100 * 365 * 24 * 60 * 60 if cache_settings.FilterForever else cache_settings.ExpireTime
        expire = int(time.time()) + expire

        cache_path = Path(cache_settings.CachePath) / self.spider.name
        cache_path.mkdir(parents=True, exist_ok=True)

        await self.done.dump_requests(path=cache_path, expire=expire, strict=False)

    async def is_valid(self, request: HttpRequest) -> bool:
        if request.dnt_filter:
            return True
        for queue in [self.waiting, self.failure, self.done]:
            if await queue.contains_request(request):
                logger.level2(msg=f'request 已存在{queue}队列中 ---> {request}')
                return False
        return True

    async def get(self, count: int) -> AsyncGenerator[HttpRequest, None]:
        if not await self.waiting.is_empty():
            requests = self.waiting.fetch_requests(count)
        elif not self.failure.is_empty():
            requests = self.failure.fetch_requests(count)
        else:
            return

        async for request in requests:
            if not (await self.pending.contains_request(request) or await self.done.contains_request(request)):
                yield await self.pending.add_request(request)

    async def update_progress(self):
        """更新并输出爬虫进度信息"""

        completed_count = await self.done_size()
        success_count = self.success_size()
        failure_count = await self.failure_size()
        pending_count = self.pending_size()
        waiting_count = await self.waiting_size()
        total_count = completed_count + pending_count + waiting_count
        progress = round(completed_count / total_count, 4) if total_count else 0

        logger.level2(
            msg=f"爬虫请求池进度更新:\n"
                f"{'=' * 50}\n"
                f"\t\t总请求数: {total_count:,}\n"
                f"\t\t完成数量: {completed_count:,} (成功: {success_count:,} | 失败: {failure_count:,})\n"
                f"\t\t进行中数量: {pending_count:,}\n"
                f"\t\t等待中数量: {waiting_count:,}\n"
                f"\t\t完成进度: {progress:.2%}\n"
                f"{'=' * 50}"
        )

        if progress == 1:
            logger.level2(msg="爬虫任务已全部完成!")
        elif progress >= 0.5 and progress < 0.51:
            logger.level2(msg="爬虫任务已完成一半!")

    async def waiting_size(self) -> int:
        return await self.waiting.get_queue_size()

    def pending_size(self) -> int:
        return self.pending.get_queue_size()

    async def done_size(self) -> int:
        return await self.done.get_queue_size()

    def success_size(self) -> int:
        return self.done.success_request_count

    async def failure_size(self):
        return self.done.failed_request_count

    async def is_empty(self):
        return await self.waiting.is_empty() and self.pending.is_empty() and self.failure.is_empty()
