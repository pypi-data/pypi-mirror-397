import inspect

from AioSpider.objects import MiddlewareType
from AioSpider.http import HttpRequest, Response
from AioSpider.exceptions import MiddlerwareException

from .spider import SpiderMiddleware


class MiddlewareManager:
    
    def __init__(self):
        self.download_middlewares = []
        self.spider_middlewares = []

    def register(self, middleware):
        if isinstance(middleware, SpiderMiddleware):
            self.spider_middlewares.append(middleware)
        else:
            self.download_middlewares.append(middleware)
            
    async def process_request(self, request: HttpRequest, type: MiddlewareType):

        if request is None:
            return None
        
        if type == MiddlewareType.download:
            middlewares = self.download_middlewares
        elif type == MiddlewareType.spider:
            middlewares = self.spider_middlewares
        else:
            raise MiddlerwareException('无效的中间件类型')

        for m in middlewares:

            if not hasattr(m, 'process_request'):
                continue

            ret = await m.process_request(request) if inspect.iscoroutinefunction(
                m.process_request) else m.process_request(request)

            if ret is None:
                continue
            elif ret is False:
                return None
            elif isinstance(ret, (HttpRequest, Response)):
                return ret
            else:
                raise MiddlerwareException('中间件返回值错误，中间件的process_request方法返回值必须为 Request/Response/None/False 对象')

        return request

    async def process_response(self, response: Response, type: MiddlewareType):

        if type == MiddlewareType.download:
            middlewares = self.download_middlewares
        elif type == MiddlewareType.spider:
            middlewares = self.spider_middlewares
        else:
            raise MiddlerwareException('无效的中间件类型')

        for m in middlewares:
            if not hasattr(m, 'process_response'):
                continue

            result = await m.process_response(response) if inspect.iscoroutinefunction(
                m.process_response) else m.process_response(response)

            if result is None:
                continue
            elif result is False:
                return None
            elif isinstance(result, (HttpRequest, Response)):
                return result
            else:
                raise MiddlerwareException('中间件返回值错误，中间件的process_response方法返回值必须为 Request/Response/None/False 对象')

        return response

    async def process_exception(self, request, exception, type: MiddlewareType):

        if exception is None:
            return None
        
        if type == MiddlewareType.download:
            middlewares = self.download_middlewares
        elif type == MiddlewareType.spider:
            middlewares = self.spider_middlewares
        else:
            raise MiddlerwareException('无效的中间件类型')

        for m in middlewares:
            if not hasattr(m, 'process_exception'):
                continue

            ret = m.process_exception(request, exception)

            if ret is None:
                continue
            elif isinstance(ret, Exception):
                raise ret
            elif isinstance(ret, (HttpRequest, Response)):
                return ret
            else:
                raise MiddlerwareException('中间件返回值错误，中间件的process_exception方法返回值必须为 Request/Response/None 对象')

        return None
