import json
import random
from pathlib import Path
from abc import ABCMeta, abstractmethod
from asyncio import exceptions

import aiohttp
import requests

from AioSpider.tools import make_timestamp
from AioSpider import logger
from AioSpider.objects import EventType
from AioSpider.http import HttpRequest, Response


class DownloadMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    def __init__(self, event_engine, spider, settings, browser=None):
        self.event_engine = event_engine
        self.spider = spider
        self.settings = settings
        self.browser = browser
        event_engine.register(EventType.SPIDER_OPEN, self.spider_open)
        event_engine.register(EventType.SPIDER_CLOSE, self.spider_close)
    
    @abstractmethod
    def process_request(self, request: HttpRequest):
        """
            处理请求
            @params:
                request: HttpRequest 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """

        return None

    @abstractmethod
    def process_response(self, response: Response):
        """
            处理响应
            @params:
                response: Response 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """
        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass

    
class ErrorMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    def __init__(self, event_engine, spider, settings, browser=None):
        self.event_engine = event_engine
        self.spider = spider
        self.settings = settings
        self.browser = browser
        event_engine.register(EventType.SPIDER_OPEN, self.spider_open)
        event_engine.register(EventType.SPIDER_CLOSE, self.spider_close)

    @abstractmethod
    def process_exception(self, request, exception):
        """
            处理异常
            @params:
                request: HttpRequest 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                exception: 将会抛出该异常
        """

        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass


class FirstMiddleware(DownloadMiddleware):
    """最先执行的中间件"""

    def process_request(self, request: HttpRequest):
        return None

    def process_response(self, response: Response):
        return None


class LastMiddleware(DownloadMiddleware):
    """最后执行的中间件"""

    def process_request(self, request: HttpRequest):
        return None

    def process_response(self, response: Response):
        return None


class RetryMiddleware(DownloadMiddleware):
    """重试中间件"""

    def process_request(self, request: HttpRequest):
        return None

    def process_response(self, response: Response):
        if hasattr(self.spider, f'process_{response.status}'):
            ret = getattr(self.spider, f'process_{response.status}')(response.request, response)
            if ret is None:
                return None
            elif isinstance(ret, HttpRequest):
                response.request = ret
            elif isinstance(ret, Response):
                response = ret
                return None
            else:
                return False

        request = response.request

        if request.retry(response.status):
            logger.level4(msg=f'状态码异常，正在进行第{request._retry_times}次重试，{response} ')
            return request

        return False


class SecMsMiddleware(LastMiddleware):

    def process_request(self, request: HttpRequest):
        request.time = make_timestamp()
        return None

    def process_response(self, response: Response):
        response.request.time = make_timestamp() - response.request.time
        if response.status == 200:
            logger.level2(msg=response)
        else:
            logger.level4(msg=response)
        return None
    

class ExceptionMiddleware(ErrorMiddleware):
    """异常中间件"""

    def process_exception(self, request, exception):

        if isinstance(exception, aiohttp.ClientPayloadError):
            logger.level5(msg=f'ClientPayloadError：{str(exception)}')
            return None
        if isinstance(exception, aiohttp.ServerDisconnectedError):
            logger.level5(msg=f'ServerDisconnectedError：{str(exception)}')
            return None
        if isinstance(exception, (aiohttp.ClientOSError, aiohttp.ClientConnectorCertificateError)):
            logger.level5(msg=f'该域名({request.url.domain})无法连接，请确保URL域名正确！')
            return None
        if isinstance(exception, aiohttp.ClientHttpProxyError):
            logger.level5(msg=f'代理认证失败：{request.proxy}')
            return self.spider.process_407(request, None)
        if isinstance(exception, aiohttp.TooManyRedirects):
            logger.level5(msg=f'TooManyRedirects：{str(exception)}')
            return None
        if isinstance(exception, exceptions.TimeoutError):
            logger.level5(
                msg=f'网络连接超时：{request}, TIMEOUT: {request.timeout or self.settings.SpiderRequestConfig.REQUEST_TIMEOUT}'
            )
            return None
        if isinstance(exception, requests.exceptions.ProxyError):
            logger.level5(
                msg=f'网络代理错误：{request}, ProxyError: {str(exception)}'
            )
            return None
        if isinstance(exception, aiohttp.ClientHttpProxyError):
            logger.level5(
                msg=f'网络代理错误或目标网站连接失败：{request}, ProxyError: {str(exception)}'
            )
            return None

        return exception
