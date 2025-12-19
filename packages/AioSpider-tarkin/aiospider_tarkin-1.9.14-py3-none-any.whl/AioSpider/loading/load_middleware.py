__all__ = ['LoadMiddleware']

from pprint import pformat
from pathlib import Path
from importlib import import_module

from AioSpider import logger
from AioSpider.exceptions import SettingsConfigException
from AioSpider.middleware import (
    DownloadMiddleware, SpiderMiddleware, FirstMiddleware, LastMiddleware, MiddlewareManager
)


class LoadMiddleware:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.init_middleware()

    def __init__(self, event_engine, spider, settings, browser):
        self.event_engine = event_engine
        self.spider = spider
        self.middleware_manager = MiddlewareManager()
        self.settings = settings
        self.browser = browser

    def init_middleware(self):

        middleware = getattr(self.settings, 'MIDDLEWARE', {})
        middleware = sorted(middleware, key=middleware.get)

        if not middleware:
            return []

        logger.level3(msg=f'已加载到{len(middleware)}个中间件：\n{pformat(middleware)}')

        instances = [self._create_middleware_instance(p) for p in middleware]

        first_last = [
            (idx, instance) for idx, instance in enumerate(instances)
            if isinstance(instance, (FirstMiddleware, LastMiddleware))
        ]

        for idx, instance in reversed(first_last):
            instances.pop(idx)
            if isinstance(instance, FirstMiddleware):
                instances.insert(0, instance)
            else:
                instances.append(instance)

        if self.browser is not None:
            from AioSpider.middleware import BrowserRenderMiddleware
            instances.insert(0, BrowserRenderMiddleware(self.event_engine, self.settings, self.browser))

        for i in instances:
            self.middleware_manager.register(i)

        return self.middleware_manager

    def _create_middleware_instance(self, p):
        
        pkg, *mid, c = p.split('.')

        if pkg in __package__:
            x = import_module(f'AioSpider.{".".join(mid)}')
            cls = getattr(x, c)
            return cls(self.event_engine, self.spider, settings=self.settings, browser=self.browser)

        if pkg == Path.cwd().name:
            try:
                x = __import__('middleware')
            except:
                x = None
            cls = getattr(x, c, None)
            if cls and (
                    issubclass(cls, DownloadMiddleware) or issubclass(cls, SpiderMiddleware)
            ):
                return cls(self.event_engine, self.spider, self.settings, self.browser)

        raise SettingsConfigException(f'{p} 中间件加载失败')
