import httpx

from AioSpider.objects import EventType
from AioSpider.downloader.abc import HttpxDownloader
from AioSpider.tools import singleton


@singleton
class HttpxSession(HttpxDownloader):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_engine.register(EventType.SESSION_CLOSE, self.close)
        self.proxy = None

    @property
    def session(self):
        if self._session is None or self._closed:
            self._session = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_connections=self.connection_pool_settings.max_connect_count,
                    max_keepalive_connections=self.connection_pool_settings.max_connect_count,
                ),
                http1=self.connection_pool_settings.http1,
                http2=self.connection_pool_settings.http2,
                verify=self.connection_pool_settings.verify,
                follow_redirects=self.connection_pool_settings.allow_redirects,
                max_redirects=self.connection_pool_settings.max_redirects,
                proxies=self.proxy
            )
            self._closed = False
        return self._session

    @HttpxDownloader.handle_request_except
    async def get(self, request, **kwargs):
        kwargs.pop('data')
        kwargs.pop('json')
        proxy = kwargs.pop('proxy')

        if proxy and self.proxy != proxy:
            self.proxy = proxy
            await self.close()

        resp = await self.session.get(**kwargs)
        return self.process_response(request, resp)

    @HttpxDownloader.handle_request_except
    async def post(self, request, **kwargs):

        proxy = kwargs.pop('proxy')

        if proxy and self.proxy != proxy:
            self.proxy = proxy
            await self.close()

        resp = self.session.post(**kwargs)
        return self.process_response(request, resp)

    async def close(self):
        if self._session:
            await self._session.aclose()
            self._session = None
            self._closed = True


class HttpxNoSession(HttpxDownloader):

    @HttpxDownloader.handle_request_except
    async def get(self, request, **kwargs):
        kwargs.pop('data')
        kwargs.pop('json')
        proxy = kwargs.pop('proxy', None)
        async with httpx.AsyncClient(proxies=proxy) as client:
            resp = await client.get(**kwargs)
        return self.process_response(request, resp)

    @HttpxDownloader.handle_request_except
    async def post(self, request, **kwargs):
        proxy = kwargs.pop('proxy', None)
        async with httpx.AsyncClient(proxies=proxy) as client:
            resp = await client.post(**kwargs)
        return self.process_response(request, resp)
