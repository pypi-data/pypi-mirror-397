import time
import random
import inspect
from functools import reduce

from AioSpider.tools import parse_json_data
from AioSpider.objects import EventType, ProxyPoolStrategy, ProxyType
from AioSpider.orm import ProxyPoolModel

from .proxy import BaseProxy, Proxy, TurnelProxy


class ProxyPool:

    def __init__(self, event_engine, settings, reload_interval: int = 300):
        self.proxies = None or []
        self.reload_interval = reload_interval
        self.settings = settings
        self._flag = False
        self._proxy_count = None
        self._weights = None
        self._weights_proxies = None
        self.start_stamp = time.time()
        event_engine.register(EventType.SPIDER_OPEN, self.spider_open)
        event_engine.register(EventType.SPIDER_OPEN, self.spider_close)

    def spider_open(self, spider):

        if self.settings.proxy_type != ProxyType.pool:
            return

        proxies = parse_json_data(self.settings.config, f'{ProxyType.pool}.from', [])

        if isinstance(proxies, BaseProxy):
            self.proxies = [proxies]
        elif isinstance(proxies, list):
            self.proxies = proxies
        elif inspect.isclass(proxies, ProxyPoolModel):
            self.proxy_model = proxies
            self._flag = True
            self.reload()
        else:
            return

    def spider_close(self, spider):
        pass

    def reload(self):
        self.proxies.clear()
        self.proxies = [Proxy(**i) for i in self.proxy_model.get_proxy()]
        self.start_stamp = time.time()

    @property
    def weights(self):
        if self._weights is None:
            weights = [i.weight for i in self.proxies]
            gcd = lambda a, b: a if b == 0 else gcd(b, a % b)
            sim_ratio = lambda x: [i // reduce(gcd, x) for i in x]
            weights = sim_ratio([int((weight / sum(weights)) * 100) for weight in weights])
            self._weights = dict(zip(self.proxies, weights))
        return self._weights

    @property
    def proxy_count(self):
        if self._proxy_count is None:
            self._proxy_count = {k: 0 for k in self.proxies}
        return self._proxy_count

    @property
    def weights_proxies(self):
        if self._weights_proxies is None:
            self._weights_proxies = [proxy for proxy in self.proxies for _ in range(self.weights[proxy])]
        return self._weights_proxies

    def get_proxy(self):

        mode = parse_json_data(self.settings.config, f'{ProxyType.pool}.mode', '')

        if self._flag and (time.time() - self.start_stamp >= self.reload_interval):
            self.reload()

        if not self.proxies:
            return None

        if mode == ProxyPoolStrategy.weight:
            return self.distribute_weighted()
        elif mode == ProxyPoolStrategy.balance:
            return self.distribute_balanced()
        elif mode == ProxyPoolStrategy.random:
            return random.choice(self.proxies)
        else:
            return self.distribute_balanced()

    def distribute_balanced(self):
        proxy = min(self.proxy_count, key=self.proxy_count.get)
        self.proxy_count[proxy] += 1
        return proxy

    def distribute_weighted(self):
        if not self.weights_proxies:
            self._weights_proxies = None
        return self.weights_proxies.pop(random.randint(0, len(self.weights_proxies) - 1))
