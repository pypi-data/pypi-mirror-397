import aiohttp

from AioSpider import logger
from AioSpider.objects import EventType
from AioSpider.downloader.abc import AiohttpDownloader
from AioSpider.tools import singleton


@singleton
class AiohttpSession(AiohttpDownloader):
    """Aiohttp会话管理类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_engine.register(EventType.SESSION_CLOSE, self.close)

    def create_connector(self):
        return aiohttp.TCPConnector(
            limit=self.connection_pool_settings.max_connect_count,
            use_dns_cache=self.connection_pool_settings.use_dns_cache,
            ttl_dns_cache=self.connection_pool_settings.ttl_dns_cache,
            limit_per_host=self.connection_pool_settings.limit_per_host,
            verify_ssl=self.connection_pool_settings.verify,
            force_close=self.connection_pool_settings.force_close,
            enable_cleanup_closed=self.connection_pool_settings.enable_cleanup_closed
        )

    @property
    def session(self):
        if self._session is None or self._closed:
            self._session = aiohttp.ClientSession(
                connector=self.create_connector(), 
                requote_redirect_url=self.connection_pool_settings.allow_redirects
            )
            self._closed = False
        return self._session

    @AiohttpDownloader.handle_request_except
    async def get(self, request, **kwargs):
        kwargs = self.process_timeout(kwargs)
        async with self.session.get(**kwargs) as resp:
            return await self.process_response(request, resp)

    @AiohttpDownloader.handle_request_except
    async def post(self, request, **kwargs):
        kwargs = self.process_timeout(kwargs)
        async with self.session.post(**kwargs) as resp:
            return await self.process_response(request, resp)

    async def close(self):
        if self._session is not None:
            await self.session.close()
            self._session = None
            self._closed = True
            logger.level3(msg="aiohttp session 会话已关闭")


class AiohttpNoSession(AiohttpDownloader):
    """无会话的Aiohttp请求类"""

    @AiohttpDownloader.handle_request_except
    async def get(self, request, **kwargs):
        kwargs = self.process_timeout(kwargs)
        async with aiohttp.request('GET', **kwargs) as resp:
            return await self.process_response(request, resp)

    @AiohttpDownloader.handle_request_except
    async def post(self, request, **kwargs):
        kwargs = self.process_timeout(kwargs)
        async with aiohttp.request('POST', **kwargs) as resp:
            return await self.process_response(request, resp)
