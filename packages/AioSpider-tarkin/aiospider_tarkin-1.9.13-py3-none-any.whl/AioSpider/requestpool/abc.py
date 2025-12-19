from abc import abstractmethod
from AioSpider.http import HttpRequest

__all__ = ['HttpRequestQueue']


class HttpRequestQueue:

    @abstractmethod
    async def add_request(self, request: HttpRequest) -> HttpRequest:
        pass

    @abstractmethod
    async def fetch_requests(self, count: int):
        pass

    @abstractmethod
    async def contains_request(self, request: HttpRequest):
        pass

    @abstractmethod
    def get_queue_size(self):
        pass

    @abstractmethod
    async def is_empty(self) -> bool:
        pass
