import requests
from requests.adapters import HTTPAdapter

from AioSpider.downloader.abc import RequestsDownloader
from AioSpider.objects import EventType
from AioSpider.tools import singleton


@singleton
class RequestsSession(RequestsDownloader):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_engine.register(EventType.SESSION_CLOSE, self.close)
        self._session = None
        self._closed = True

    @property
    def session(self):
        if self._session is None or self._closed:
            self._session = requests.Session()
            self._session.verify = self.connection_pool_settings.verify
            self._session.max_redirects = self.connection_pool_settings.max_redirects
            adapter = HTTPAdapter(
                pool_connections=self.connection_pool_settings.max_connect_count,
                pool_maxsize=self.connection_pool_settings.max_connect_count,
                max_retries=self.connection_pool_settings.max_retries,
                pool_block=self.connection_pool_settings.pool_block
            )

            for protocol in ("http://", "https://"):
                self._session.mount(protocol, adapter)

            self._closed = False

        return self._session

    @RequestsDownloader.handle_request_except
    async def get(self, request, **kwargs):
        res =  self.session.get(**kwargs)
        return self.process_response(request, res)

    @RequestsDownloader.handle_request_except
    async def post(self, request, **kwargs):
        res =  self.session.post(**kwargs)
        return self.process_response(request, res)

    async def close(self):
        if self._session:
            self._session.close()
            self._session = None
            self._closed = True


class RequestsNoSession(RequestsDownloader):

    @RequestsDownloader.handle_request_except
    async def get(self, request, **kwargs):
        return self.process_response(request, requests.get(**kwargs))

    @RequestsDownloader.handle_request_except
    async def post(self, request, **kwargs):
        return self.process_response(request, requests.post(**kwargs))
