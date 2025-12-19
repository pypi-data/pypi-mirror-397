import random
from abc import ABCMeta, abstractmethod

from AioSpider.objects import EventType, ProxyType
from urllib.request import getproxies
from AioSpider.http import Response
from AioSpider.tools import parse_json_data

from .user_pool.pool import UserPool
from .proxy_pool.pool import ProxyPool


class SpiderMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    def __init__(self, event_engine, spider, settings, browser=None):
        self.event_engine = event_engine
        self.spider = spider
        self.settings = settings
        self.browser = browser
        event_engine.register(EventType.SPIDER_OPEN, self.spider_open)
        event_engine.register(EventType.SPIDER_CLOSE, self.spider_close)

    @abstractmethod
    def process_request(self, request):
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
    def process_response(self, response):
        """
            处理请求
            @params:
                response: Response 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """

        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass


class UserPoolMiddleware(SpiderMiddleware):

    def __init__(self, event_engine, spider, settings, browser=None):
        self.user_pool = UserPool(event_engine)
        super().__init__(event_engine=event_engine, spider=spider, settings=settings, browser=browser)

    def process_request(self, request):

        if self.user_pool.users is None:
            return None

        if request.cookies is None:
            request.cookies = self.user_pool.get_user_cookies()
        else:
            request.cookies.update(self.user_pool.get_user_cookies())

        return None

    def process_response(self, response):
        return None
    
    
class ProxyPoolMiddleware(SpiderMiddleware):

    def __init__(self, event_engine, spider, settings, browser=None):
        self.proxy_pool = ProxyPool(event_engine, settings.RequestProxyConfig)
        super().__init__(event_engine, spider=spider, settings=settings, browser=browser)

    def process_request(self, request):

        conf = self.settings.RequestProxyConfig

        if conf.proxy_type is ProxyType.none:
            return None
        elif conf.proxy_type == ProxyType.system:
            request.proxy = getproxies().get('http') or getproxies().get('https')
        elif conf.proxy_type == ProxyType.appoint:
            address = parse_json_data(conf.config, ProxyType.appoint.value, None)
            request.proxy = (
                 str(random.choice(address)) if isinstance(address, (list, tuple)) else str(address)
            )
        elif conf.proxy_type == ProxyType.pool:
            proxy = self.proxy_pool.get_proxy()
            request.proxy = str(proxy) if proxy else None
        else:
            return None

        return None

    def process_response(self, response):
        return None


class BrowserRenderMiddleware(SpiderMiddleware):

    def process_request(self, request):

        if request.render:
            return Response(request=request, browser=self.browser)

        return None

    def process_response(self, response):
        return None

