from enum import Enum, auto
from pathlib import Path

__all__ = [
    'Path',
    'PathConstant',
    'BackendEngine',
    'PaddingMode',
    'AESMode',
    'ModelNameType',
    'SleepStrategy',
    'DataFilterMethod',
    'UserType',
    'EventType',
    'By',
    'EnvType',
    'MiddlewareType',
    'Priority',
]


class PathConstant:
    HOME = Path.home()


class BackendEngine:
    queue = 'queue'
    redis = 'redis'


class BrowserType:
    chromium = 'chromium'
    firefox = 'firefox'


class PaddingMode:
    NoPadding = 0
    ZeroPadding = 1
    PKCS7Padding = 2


class AESMode(Enum):
    ECB = 1
    CBC = 2
    CFB = 3
    OFB = 5
    CTR = 6
    OPENPGP = 7
    CCM = 8
    EAX = 9
    SIV = 10
    GCM = 11
    OCB = 12


class ModelNameType:
    lower = 'lower'
    upper = 'upper'
    smart = 'smart'


class By:
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"


class SleepStrategy:
    fixed = 'fixed'
    random = 'random'


class DataFilterMethod:
    """数据去重方式"""

    dqset = 'dqset'
    bloom = 'bloom'
    redisSet = 'redisSet'
    redisBloom = 'redisBloom'


class MiddlewareType:
    """中间件类型"""
    download = 1
    spider = 2


class Priority(Enum):
    LOW = 0             # 低
    NORMAL = 1          # 普通
    HIGH = 2            # 高


class EventType(Enum):
    """事件类型"""
    TIMER = auto()  # 定时事件
    SPIDER_OPEN = auto()  # 爬虫开启事件
    SPIDER_CLOSE = auto()  # 爬虫结束事件
    BROWSER_QUIT = auto()  # 浏览器退出事件
    REQUEST_CLOSE = auto()  # 请求池关闭事件
    WAITING_CLOSE = auto()  # waiting队列关闭事件
    PENDING_CLOSE = auto()  # pending队列关闭事件
    FAILURE_CLOSE = auto()  # failure队列关闭事件
    DONE_CLOSE = auto()  # done队列关闭事件
    CONNECTION_CLOSE = auto()  # 连接关闭事件
    DATABASE_CLOSE = auto()  # 数据库关闭事件
    SESSION_CLOSE = auto()  # 会话关闭事件
    LOAD_CONFIG_START = auto()  # 配置加载前事件
    LOAD_CONFIG_STOP = auto()  # 配置加载后事件


class UserType(Enum):
    """用户类型"""

    visitor = 1
    normal = 2
    vip = 3


class EnvType(Enum):
    """环境"""
    production = '生产环境'
    debug = '调试环境'
