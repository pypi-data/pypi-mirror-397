import asyncio
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

import aiohttp
import httpx
import requests

from AioSpider import logger
from AioSpider.objects import HttpMethod
from AioSpider.exceptions import RequestException
from AioSpider.http import HttpRequest, Response

__all__ = [
    'RequestsDownloader', 
    'AiohttpDownloader', 
    'HttpxDownloader'
]


class AbstractDownloader(ABC):
    """基础元类,定义了下载器的通用接口和方法"""

    def __init__(self, event_engine, request_settings: Dict[str, Any], connection_pool_settings: Dict[str, Any]):
        self.event_engine = event_engine
        self.request_settings = request_settings
        self.connection_pool_settings = connection_pool_settings

    async def __call__(self, request: HttpRequest, *args, **kwargs) -> Response:
        return await self.request(request)

    async def request(self, request: HttpRequest) -> Response:
        """处理请求的主要方法"""
        if not request.url.scheme or not request.url.domain:
            raise RequestException(f'无效的请求URL，URL: {request.url.url}')

        attrs = self.query_attrs(request)
        attrs = self.handle_proxy(attrs)
        method = attrs.pop('method')
        
        if HttpMethod(method) == HttpMethod.GET:
            return await self.get(request, **attrs)
        elif HttpMethod(method) == HttpMethod.POST:
            return await self.post(request, **attrs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def query_attrs(self, request: HttpRequest) -> Dict[str, Any]:
        """从请求对象中提取属性"""
        attrs = request.to_request_dict() if request else {}

        # 如果 timeout 为 None，使用 settings 的默认值
        if attrs.get('timeout') is None:
            attrs['timeout'] = self.request_settings.REQUEST_TIMEOUT

        return attrs
    
    @staticmethod
    def handle_request_except(func):
        """处理请求异常的装饰器"""
        async def wrapper(self, request, **kwargs):
            times = max(1, self.request_settings.REQUEST_ERROR_RETRY_TIMES)
            exception = None
            for index in range(times):
                try:
                    return await func(self, request, **kwargs)
                except RuntimeError as e:
                    if 'Session is closed' in str(e):
                        self._closed = True
                        logger.level4(msg=f'{request} 请求异常，Session 被异常关闭，正在自动处理...')
                        return await func(self, request, **kwargs)
                    else:
                        exception = e
                        logger.level5(msg=f'{request} 请求异常，正在进行第{index+1}次重试，异常原因：RuntimeError - {e}')
                except aiohttp.ClientError as e:
                    exception = e
                    logger.level5(msg=f'{request} 请求异常，正在进行第{index+1}次重试，异常原因：ClientError - {e}')
                except httpx.HTTPError as e:
                    exception = e
                    logger.level5(msg=f'{request} 请求异常，正在进行第{index+1}次重试，异常原因：HTTPError - {e}')
                except Exception as e:
                    exception = e
                    logger.level5(msg=f'{request} 请求异常，正在进行第{index+1}次重试，异常原因：未知错误 - {e}')
                await asyncio.sleep(self.request_settings.REQUEST_ERROR_RETRY_SLEEP)
            return exception
        return wrapper

    @abstractmethod
    async def get(self, request: HttpRequest, **kwargs) -> Response:
        pass

    @abstractmethod
    async def post(self, request: HttpRequest, **kwargs) -> Response:
        pass

    async def close(self):
        pass

    @staticmethod
    @abstractmethod
    def handle_proxy(attrs: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def process_response(self, req: HttpRequest, resp: Any) -> Response:
        pass


class RequestsDownloader(AbstractDownloader):
    """Requests库的元类"""

    def __init__(self, event_engine, request_settings: Dict[str, Any], connection_pool_settings: Dict[str, Any]):
        super().__init__(event_engine, request_settings, connection_pool_settings)
        self._session: Optional[requests.Session] = None
        self._closed: bool = True

    @staticmethod
    def handle_proxy(attrs: Dict[str, Any]) -> Dict[str, Any]:
        proxy = attrs.pop('proxy', None)
        if not proxy:
            attrs['proxies'] = None
        else:
            attrs['proxies'] = {
                'http': f'http://{proxy}' if 'http' not in proxy else proxy,
                'https': f'http://{proxy}' if 'http' not in proxy else proxy
            }
        return attrs
    
    def process_response(self, req: HttpRequest, resp: requests.Response) -> Response:
        return Response(
            status=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
            request=req
        )


class AiohttpDownloader(AbstractDownloader):
    """Aiohttp库的元类"""

    def __init__(self, event_engine, request_settings: Dict[str, Any], connection_pool_settings: Dict[str, Any]):
        super().__init__(event_engine, request_settings, connection_pool_settings)
        self._session: Optional[aiohttp.ClientSession] = None
        self._closed: bool = True

    def query_attrs(self, request: HttpRequest) -> Dict[str, Any]:
        attrs = super().query_attrs(request)
        if 'timeout' in attrs and isinstance(attrs['timeout'], (int, float)):
            attrs['timeout'] = aiohttp.ClientTimeout(total=int(attrs['timeout']))
        return attrs
    
    @staticmethod
    def handle_proxy(attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get('proxy') and 'http' not in attrs['proxy']:
            attrs['proxy'] = f'http://{attrs["proxy"]}'
        return attrs
    
    def process_timeout(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        timeout = kwargs.pop('timeout', None)
        if timeout is not None:
            # 检查是否已经是 ClientTimeout 对象，避免重复转换
            if not isinstance(timeout, aiohttp.ClientTimeout):
                kwargs['timeout'] = aiohttp.ClientTimeout(total=timeout)
            else:
                kwargs['timeout'] = timeout
        return kwargs
    
    async def process_response(self, req: HttpRequest, resp: aiohttp.ClientResponse) -> Response:
        return Response(
            status=resp.status,
            headers=dict(resp.headers),
            cookies=dict(resp.cookies),
            content=await resp.read(),
            request=req
        )


class HttpxDownloader(AbstractDownloader):
    """Httpx库的元类"""

    def __init__(self, event_engine, request_settings: Dict[str, Any], connection_pool_settings: Dict[str, Any]):
        super().__init__(event_engine, request_settings, connection_pool_settings)
        self._session: Optional[httpx.AsyncClient] = None
        self._closed: bool = True

    @staticmethod
    def handle_proxy(attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get('proxy') and 'http' not in attrs['proxy']:
            attrs['proxy'] = f'http://{attrs["proxy"]}'
        return attrs

    def process_response(self, req: HttpRequest, resp: httpx.Response) -> Response:
        return Response(
            status=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
            request=req
        )
