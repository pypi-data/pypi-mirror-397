from AioSpider.objects import RequestWay
from AioSpider.exceptions import RequestException

from .aiohttp_module import AiohttpSession, AiohttpNoSession
from .requests_module import RequestsSession, RequestsNoSession
from .httpx_module import HttpxSession, HttpxNoSession


def downloader_factory(event_engine, request_settings, connection_pool_settings):
    handler_map = {
        (None, True): (AiohttpSession, connection_pool_settings.Aiohttp),
        (None, False): (AiohttpNoSession, connection_pool_settings.Aiohttp),
        (RequestWay.aiohttp, True): (AiohttpSession, connection_pool_settings.Aiohttp),
        (RequestWay.aiohttp, False): (AiohttpNoSession, connection_pool_settings.Aiohttp),
        (RequestWay.requests, True): (RequestsSession, connection_pool_settings.Requests),
        (RequestWay.requests, False): (RequestsNoSession, connection_pool_settings.Requests),
        (RequestWay.httpx, True): (HttpxSession, connection_pool_settings.Httpx),
        (RequestWay.httpx, False): (HttpxNoSession, connection_pool_settings.Httpx)
    }
    handler, config = handler_map.get(
        (request_settings.REQUEST_USE_METHOD, request_settings.REQUEST_USE_SESSION)
    )
    assert handler is not None, RequestException("请求库配置不正确，请检查配置文件")

    return handler(event_engine, request_settings, config)


class Downloader:

    def __init__(self, event_engine, request_settings, connection_pool_settings, middleware):
        self._downloader = downloader_factory(event_engine, request_settings, connection_pool_settings)
        self.middleware = middleware

    async def fetch(self, request):
        return await self._downloader(request)
