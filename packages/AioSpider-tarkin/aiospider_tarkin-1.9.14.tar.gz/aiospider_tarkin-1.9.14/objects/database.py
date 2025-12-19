from attr import define, field
from enum import Enum
from typing import Union, Optional
from pathlib import Path

__all__ = [
    'TableType',
    'DataBaseType',
    'WriteMode',
    'DatabaseEngine',
    'DatabaseCharset',
    'ConnectionData',
    'SqliteConnectionData',
    'MysqlConnectionData',
    'CsvConnectionData',
    'MongoConnectionData',
    'RedisConnectionData',
    'FileConnectionData',
    'AdapterResultType'
]


class TableType(Enum):
    """表类型"""
    data = '数据表'
    task = '任务表'
    task_progress = '任务进度表'
    spider = '爬虫表'
    table = '表表'
    proxy = '代理表'
    statistics = '统计表'
    notice = '预警表'


class DataBaseType(Enum):
    mysql = 'Mysql'
    sqlite = 'Sqlite'
    sqlserver = 'Sqlserver'
    postgresql = 'Postgresql'
    oracle = 'Oracle'
    mariadb = 'Mariadb'
    csv = 'Csv'
    file = 'File'
    mongodb = 'Mongodb'
    redis = 'Redis'


class WriteMode(Enum):
    A = 'a'         # 追加模式
    W = 'w'         # 覆盖模式
    WB = 'wb'       # 二进制写模式


class DatabaseEngine(Enum):
    none = 'none'
    InnoDB = 'InnoDB'
    MyISAM = 'MyISAM'
    MEMORY = 'MEMORY'
    ARCHIVE = 'ARCHIVE'
    CSV = 'CSV'
    BLACKHOLE = 'BLACKHOLE'
    MERGE = 'MERGE'
    FEDERATED = 'FEDERATED'


class DatabaseCharset(Enum):
    utf8mb3 = 'utf8mb3'
    utf8mb4 = 'utf8mb4'
    utf8 = 'utf8'
    latin1 = 'latin1'
    ascii = 'ascii'
    utf16 = 'utf16'
    utf32 = 'utf32'


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class ConnectionData:
    alias: str = field()
    engine: Union[DatabaseEngine, str] = field(
        default=DatabaseEngine.none,
        converter=lambda x: x.value if isinstance(x, DatabaseEngine) else x
    )
    charset: Union[DatabaseCharset, str] = field(
        default=DatabaseCharset.utf8,
        converter=lambda x: x.value if isinstance(x, DatabaseCharset) else x
    )

    def get_data(self):
        return {}


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class SqliteConnectionData(ConnectionData):
    path: Union[Path, str] = field(converter=lambda x: Path(x) if isinstance(x, str) else x)
    db: str = field(converter=lambda x: x + '.db3' if '.db' not in x or '.sqlite' not in x else x)
    # 每批允许写入最大字节数
    size: int = field(default=20 * 1024 * 1024)
    timeout: int = field(default=10)

    def get_data(self):
        self.path.mkdir(parents=True, exist_ok=True)
        return {
            'path': self.path / self.db,
            'chunk_size': self.size,
            'timeout': self.timeout
        }


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class MysqlConnectionData(ConnectionData):
    engine: Union[DatabaseEngine, str] = field(
        default=DatabaseEngine.InnoDB,
        converter=lambda x: x.value if isinstance(x, DatabaseEngine) else x
    )
    charset: Union[DatabaseCharset, str] = field(
        default=DatabaseCharset.utf8mb4,
        converter=lambda x: x.value if isinstance(x, DatabaseCharset) else x
    )

    host: str = field(default='127.0.0.1')
    port: int = field(default=3306)
    db: str = field()
    username: str = field()
    password: str = field()
    timeout: int = field(default=3)
    timezone: str = field(default='+8:00')
    min_connect_size: int = field(default=10)
    max_connect_size: int = field(default=20)

    def get_data(self):
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'user': self.username,
            'password': self.password,
            'charset': self.charset,
            'connect_timeout': self.min_connect_size,
            'time_zone': self.timezone,
        }


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class CsvConnectionData(ConnectionData):
    path: Union[Path, str] = field(converter=lambda x: Path(x) if isinstance(x, str) else x)

    def get_data(self):
        return {
            'path': self.path,
            'encoding': self.charset,
        }


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class MongoConnectionData(ConnectionData):
    host: str = field(default='127.0.0.1')
    port: int = field(default=27017)
    db: str = field()
    # 用于验证的数据库名称，通常是存储用户名和密码的数据库 默认 admin
    auth_db: str = field(default='admin')
    username: str = field()
    password: str = field()
    min_connect_size: int = field(default=10)
    max_connect_size: int = field(default=20)
    # 一个连接在连接池中空闲多久后会被关闭，单位秒 0: 不关闭
    max_idle_time: int = field(default=0)

    def get_data(self):
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'auth_db': self.auth_db,
            'username': self.username,
            'password': self.password,
        }


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class FileConnectionData(ConnectionData):
    path: Union[Path, str] = field(converter=lambda x: Path(x) if isinstance(x, str) else x)
    mode: WriteMode = field(default=WriteMode.WB)

    def get_data(self):
        return {
            'path': self.path,
            'encoding': self.charset,
            'mode': self.mode,
        }


@define(kw_only=True, slots=True, frozen=True, unsafe_hash=True)
class RedisConnectionData(ConnectionData):
    host: str = field(default='127.0.0.1')
    port: int = field(default=6379)
    db: int = field(default=0)
    username: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)
    max_connect_size: int = field(default=1 * 10000)

    def get_data(self):
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'username': self.username,
            'password': self.password,
            'encoding': self.charset,
            'max_connect_size': self.max_connect_size,
        }


class AdapterResultType(Enum):
    lastrowid = 'lastrowid'
    affected_rows = 'affected_rows'
    rowcount = 'rowcount'
    insertid = 'insertid'
