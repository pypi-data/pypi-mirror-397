import random
import json
from pathlib import Path

from AioSpider.objects import *

__all__ = [
    'AioSpiderPath',
    'LoggingConfig', 
    'SpiderRequestConfig', 
    'ConcurrencyStrategyConfig',
    'ConnectPoolConfig', 
    'RequestProxyConfig', 
    'MIDDLEWARE', 
    'DataFilterConfig', 
    'RequestFilterConfig', 
    'BrowserConfig', 
    'DataBaseConfig'
]


# ---------------------------------- 系统相关配置 ---------------------------------- #
DEBUG = True                                            # 调试模式
AioSpiderPath = Path(__file__).parent                   # 工作路径


class LoggingConfig:
    """日志配置"""

    class Console:
        enabled = True                                 # 是否打印到控制台
        format = Formater.A                            # 日志格式
        time_format = TimeFormater.A                   # 时间格式
        level = LogLevel.LEVEL1                        # 日志等级

    class File:
        enabled = True                                 # 是否写文件
        path = AioSpiderPath / "log"                   # 日志存储路径
        format = Formater.A                            # 日志格式
        time_format = TimeFormater.A                   # 时间格式
        level = LogLevel.LEVEL1                        # 日志等级
        mode = WriteMode.A                             # 写文件的模式
        size = 50 * 1024 * 1024                        # 每个日志文件的默认最大字节数
        encoding = 'utf-8'                             # 日志文件编码
        retention = '1 week'                           # 日志保留时间
        compression = True                             # 是否将日志压缩

    class Robot:
        dingding_robot = DingDingRobotData(enabled=False, token='')
        wechat_robot = WechatRobotData(enabled=False, token='')
        email_robot = EmailRobotData(enabled=False, token='', sender='')


# -------------------------------------------------------------------------------- #


# ---------------------------------- 爬虫相关配置 ---------------------------------- #

class SpiderRequestConfig:
    """爬虫请求配置"""

    REQUEST_USE_SESSION = False                     # 使用会话
    REQUEST_USE_METHOD = RequestWay.aiohttp         # 使用 aiohttp 库进行请求

    REQUEST_CONCURRENCY_SLEEP = {
        'strategy': SleepStrategy.fixed,
        'sleep': 1
    }                                               # 单位秒，每 task_limit 个请求休眠n秒
    PER_REQUEST_SLEEP = {
        'strategy': SleepStrategy.fixed,
        'sleep': 0
    }                                               # 单位秒，每并发1个请求时休眠1秒
    REQUEST_TIMEOUT = 5 * 60                        # 请求最大超时时间
    
    # 请求报错重试
    REQUEST_ERROR_RETRY_TIMES = 3                   # 请求报错重试次数
    REQUEST_ERROR_RETRY_SLEEP = 1                   # 请求报错重试间隔

    # 请求状态码异常重试
    MAX_STATUS_RETRY_TIMES = 3                      # 请求状态码异常最大重试次数
    RETRY_STATUS = [400, 403, 404, 500, 503]        # 请求状态码异常重试状态码列表
    
    # 请求失败重试
    MAX_FAILURE_RETRY_TIMES = 3                     # 请求失败最大重试次数

    DepthPriority = True                            # 深度优先

    # 默认请求头，优先级：spider headers > 默认headers > random headers
    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    USER_AGENT_TYPE = UserAgent.CHROME
    user_agent = json.load((Path(__file__).parent / "user-agent.json").open())

    @classmethod
    def get_user_agent(cls):
        if isinstance(cls.USER_AGENT_TYPE, str):
            return random.choice(cls.user_agent['browsers'][cls.USER_AGENT_TYPE])
        elif hasattr(cls.USER_AGENT_TYPE, '__iter__'):
            random_type = random.choice(cls.USER_AGENT_TYPE)
            return random.choice(cls.user_agent['browsers'][random_type])
        return None
    
    @classmethod
    def get_headers(cls):
        return cls.HEADERS


class ConcurrencyStrategyConfig:
    """
    爬虫并发策略. auto 自动模式，系统不干预；random 随机模式，并发速度随机于最大和最
    小并发速度之间；smart 智能模式，系统自动调节
    """

    auto = {
        'enabled': False,                       # 是否启用
        'reference_limit': 20,                  # 基准并发数量 单位：个/秒
        'wave': 5,                              # 在基准上上下波动5分之一
    }
    random = {
        'enabled': False,                       # 是否启用
        'min_limit': 10,                        # 最小并发数量 单位：个/秒
        'max_limit': 30,                        # 最小并发数量 单位：个/秒
    }
    speed = {
        'enabled': False,                       # 是否启用
        'avg_speed': 20,                        # 平均并发速度 单位：个
    }
    time = {
        'enabled': True,                       # 是否启用
        'second': 3 * 60,                       # 运行时间
        'min_limit': 10,                        # 最小并发数量 单位：个/秒
        'max_limit': 30,                        # 最小并发数量 单位：个/秒
    }
    fix = {
        'enabled': False,                        # 是否启用
        'task_limit': 50                        # 任务并发数
    }


class ConnectPoolConfig:
    """连接池"""

    class Aiohttp:
        max_connect_count = 100             # 请求最大连接数，指定为 None 时无限制
        use_dns_cache = True                # 使用内部DNS映射缓存，设置为 True 可以提高性能，减少 DNS 查询次数
        ttl_dns_cache = 10                  # DNS 缓存时间（秒），None 表示永不过期
        verify = None                       # ssl证书验证，None 使用默认设置
        limit_per_host = 0                  # 同一端点并发连接总数，同一端点是具有相同 host、port、ssl 信息，如果是0则不做限制
        force_close = False                 # 连接释放后关闭底层网络套接字
        enable_cleanup_closed = False       # 是否启用清理已关闭的 SSL 传输，需要及时清理已关闭的连接时
        allow_redirects = True              # 是否跟随重定向
    
    class Requests:
        max_connect_count = 10              # 连接池最大连接数
        max_retries = 3                     # DNS 查找失败、套接字连接失败和连接超时尝试的连接最大重试次数
        pool_block = False                  # 连接池在没有可用连接时是否应阻塞请求
        verify = True                       # ssl证书验证，None 使用默认设置
        max_redirects = 3                   # 最大重定向次数

    class Httpx:
        max_connect_count = 10              # 连接池最大连接数
        verify = True                       # ssl证书验证，None 使用默认设置
        http1 = True                        # 是否使用http1.1
        http2 = False                       # 是否使用http2
        allow_redirects = True              # 是否跟随重定向
        max_redirects = 3                   # 最大重定向次数


class RequestProxyConfig:
    """代理配置"""

    proxy_type = ProxyType.none                             # 代理类型
    config = {
        'appoint': None,                                    # 手动代理地址，支持 str、list、tuple。未加协议自动补齐成http协议，None表示不适用代理
        'pool': {
            'mode': ProxyPoolStrategy.balance,          # 代理池分配策略
            'from': None,                                   # 代理来源
        },
    }

# -------------------------------------------------------------------------------- #


# ---------------------------------- 中间件相关配置 --------------------------------- #

MIDDLEWARE = {
    "AioSpider.middleware.download.SecMsMiddleware": 110,               # 请求计时中间件
    "AioSpider.middleware.download.RetryMiddleware": 120,               # 请求重试中间件
    "AioSpider.middleware.download.ExceptionMiddleware": 130,           # 异常中间件
}

# -------------------------------------------------------------------------------- #


# ---------------------------------- 去重相关配置 ---------------------------------- #

class DataFilterConfig:
    """数据去重"""

    TASK_LIMIT = 20                                          # 数据提交并发数
    COMMIT_SIZE = 1000                                       # 数据每批提交保存的数量
    MODEL_NAME_TYPE = 'smart'                                # lower / upper / smart，处理表名的方式

    ENABLED = False                                          # 是否启用数据去重
    LoadDataFromDB = False                                   # 从数据库加载含有唯一索引数据作为种子数据去重
    FILTER_METHOD = DataFilterMethod.dqset                   # 数据去重方式
    BLOOM_INIT_CAPACITY = 10000                              # 布隆过滤器数据容量
    BLOOM_ERROR_RATE = 0.001                                 # 布隆过滤器误判率
    BLOOM_MAX_CAPACITY = 5000 * 10000                        # 布隆过滤器数据容量


class RequestFilterConfig:
    """请求去重"""

    Enabled = True,                                          # 是否缓存爬过的请求 将爬过的请求缓存到本地
    LoadSuccess = True                                       # 将CACHED_REQUEST缓存中成功的请求加载到队列
    ExpireTime = 60 * 60 * 24                                # 缓存时间 秒
    CachePath = AioSpiderPath / "cache"                      # 数据和资源缓存路径
    FilterForever = True                                     # 是否永久去重，配置此项 CACHED_EXPIRE_TIME 无效

# -------------------------------------------------------------------------------- #


# ---------------------------------- 浏览器相关配置 ---------------------------------- #

class BrowserConfig:
    """浏览器配置"""

    class Chromium:

        enabled = False                                      # 是否开启浏览器
        LogLevel = 3                                         # 日志等级
        Proxy = None                                         # 代理
        headless = False                                     # 是否无头模式
        Options = None                                       # 启动参数
        UserAgent = None                                     # user_agent
        ProfilePath = None                                   # 用户数据路径
        ExtensionPath = None                                 # 拓展应用路径
        DisableImages = False                                # 禁用图片
        DisableJavaScript = False                            # 禁用js
        DownloadPath = AioSpiderPath / "download"            # 下载路径
        ImplicitlyWait = 0                                   # 隐式等待时间

    class Firefox:

        enabled = False                                      # 是否开启浏览器
        LogLevel = 3                                         # 日志等级
        Proxy = None                                         # 代理
        headless = False                                     # 是否无头模式
        Options = None                                       # 启动参数
        UserAgent = None                                     # user_agent
        ProfilePath = None                                   # 用户数据路径
        ExtensionPath = None                                 # 拓展应用路径
        DisableImages = False                                # 禁用图片
        DisableJavaScript = False                            # 禁用js
        DownloadPath = AioSpiderPath / "download"            # 下载路径
        ImplicitlyWait = 0                                   # 隐式等待时间

# -------------------------------------------------------------------------------- #


# --------------------------------- 数据库相关配置 --------------------------------- #

class DataBaseConfig:
    """数据库配置"""

    class Csv:
        enabled = False                                         # 是否启用
        connect = [
            CsvConnectionData(
                alias='DEFAULT',
                path= AioSpiderPath / 'data',		            # 数据目录
                charset='utf-8',					            # 文件写入编码
            )
        ]

    class Sqlite:
        enabled = True
        connect = [
            SqliteConnectionData(
                alias='DEFAULT',
                path=PathConstant.HOME / '.aioSpider/data',	    # 数据库目录
                db="aioSpider",			 	                    # 数据库名称
                size=20 * 1024 * 1024,		  	                # 每批允许写入最大字节数
                timeout=10						                # 连接超时时间
            )
        ]

    class Mysql:
        enabled = False
        connect = []

    class Mongodb:
        enabled = False
        connect = []

    class File:
        enabled = False
        connect = [
            FileConnectionData(
                alias='DEFAULT',
                path= AioSpiderPath / 'data',		            # 数据目录
                charset='utf-8',					            # 文件写入编码
                mode=WriteMode.WB                               # 文件写入模式
            )
        ]

    class Redis:
        enabled = False
        connect = [
            RedisConnectionData(
                alias='DEFAULT',
                host='127.0.0.1',  			                    # 域名
                port=6379,					                    # 端口
                username=None,				                    # 用户名
                password=None,				                    # 密码
                db=0,						                    # 数据库索引
                charset='utf-8', 			                    # 编码
                max_connect_size=1 * 10000                      # 最大连接数
            )
        ]

# -------------------------------------------------------------------------------- #
