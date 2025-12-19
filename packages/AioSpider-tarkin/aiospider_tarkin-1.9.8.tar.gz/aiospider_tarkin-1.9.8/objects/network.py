from enum import Enum, auto

__all__ = [
    'UserAgent',
    'RequestWay',
    'HttpMethod',
    'ProxyType', 
    'ProxyPoolStrategy',
    'RequestStatus'
]


class UserAgent(Enum):
    """日志轮询间隔常量"""

    CHROME = 'chrome'
    FIREFOX = 'firefox'
    EDGE = 'edge'
    IE = 'ie'
    OPERA = 'opera'
    FF = 'ff'
    SAFARI = 'safari'


class RequestWay(Enum):
    aiohttp = 'aiohttp'
    requests = 'requests'
    httpx = 'httpx'


class HttpMethod(Enum):
    """请求方法"""
    GET = 'GET'
    POST = 'POST'


class ProxyType(Enum):
    none = None             # 不使用代理
    system = 'system'       # 使用系统代理
    pool = 'pool'           # 使用AioSpider内置代理池
    appoint = 'appoint'     # 手动指定proxy_pool


class ProxyPoolStrategy(Enum):
    random = 'random'       # 随机模式
    balance = 'balance'     # 均衡负载模式
    weight = 'weight'       # 按权分配模式


class RequestStatus(Enum):
    before = auto()         # 未开始
    running = auto()        # 请求中
    success = auto()        # 成功
    failed = auto()         # 失败
