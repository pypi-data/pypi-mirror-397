import asyncio
import time
from typing import Any, Optional, List, Dict
from functools import wraps

try:
    import psycopg2
    from psycopg2.extras import DictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    DictCursor = None

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None

from AioSpider import logger
from AioSpider.objects import AdapterResultType

from .adapter import DatabaseAdapter, AsyncDatabaseAdapter

__all__ = ['PostgreSQLAdapter', 'AsyncPostgreSQLAdapter']


def handle_db_error(e, sql: str, params):
    """处理数据库错误并打印信息"""
    error_type = type(e).__name__
    error_code = e.pgcode
    error_message = str(e)
    logger.level5(msg=f"PostgreSQL {error_type}. 错误代码: {error_code}, 错误信息: {error_message}, SQL: {sql}, 参数: {params}")


def ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._conn is None or self._conn.closed or (time.time() - self._last_use_time > self.max_idle_time):
            self.connect()
        return func(self, *args, **kwargs)

    return wrapper


def async_ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self._lock:
            if self._pool is None or self._pool.is_closed() or (time.time() - self._last_use_time > self.max_idle_time):
                await self.connect()
        return await func(self, *args, **kwargs)

    return wrapper


def return_data(conn, cursor, return_type, affected_rows):
    """根据返回类型返回数据"""
    if return_type == AdapterResultType.lastrowid:
        return cursor.fetchone()[0]  # PostgreSQL不支持lastrowid，这里假设返回的是自增ID
    elif return_type == AdapterResultType.affected_rows:
        return affected_rows
    elif return_type == AdapterResultType.rowcount:
        return cursor.rowcount
    elif return_type == AdapterResultType.insertid:
        return cursor.fetchone()[0]  # PostgreSQL不支持insert_id，这里假设返回的是自增ID
    else:
        return None


class PostgreSQLAdapter(DatabaseAdapter):
    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 5432, max_idle_time: int = 5 * 60 * 60, connect_timeout=5
    ):
        super().__init__()
        self.max_idle_time = float(max_idle_time)
        self._db_args = self._prepare_db_args(
            host, db, user, password, port, connect_timeout
        )
        self._conn = None
        self._last_use_time = time.time()

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(**config)

    def _prepare_db_args(self, host, db, user, password, port, connect_timeout):
        args = {
            'dbname': db,
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'connect_timeout': connect_timeout
        }
        return args

    def connect(self):
        """重新连接数据库"""
        try:
            self._conn = psycopg2.connect(**self._db_args)
        except (ConnectionError, TimeoutError) as e:
            logger.level5(msg=f"PostgreSQL数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._conn.autocommit = True
        self._last_use_time = time.time()

    @ensure_connected
    def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> Dict[str, Any]:
        """执行sql语句"""
        with self._conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                cursor.execute(sql, params)
                affected_rows = cursor.rowcount
                self._conn.commit()
                return return_data(self._conn, cursor, return_type, affected_rows)
            except psycopg2.Error as e:
                handle_db_error(e, sql, params)
                self._conn.rollback()
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
                self._conn.rollback()
            finally:
                self._conn.rollback()

    @ensure_connected
    def execute_many(self, sql: str, params: List[tuple], return_type=AdapterResultType.affected_rows) -> int:
        """执行多条sql语句"""
        with self._conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                cursor.executemany(sql, params)
                affected_rows = cursor.rowcount
                self._conn.commit()
                return return_data(self._conn, cursor, return_type, affected_rows)
            except psycopg2.Error as e:
                handle_db_error(e, sql, params)
                self._conn.rollback()
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
                self._conn.rollback()
            finally:
                self._conn.rollback()
                return 0

    @ensure_connected
    def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询并获取单个结果"""
        with self._conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                cursor.execute(sql, params)
                return cursor.fetchone()
            except psycopg2.Error as e:
                handle_db_error(e, sql, params)
                return None

    @ensure_connected
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        with self._conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                cursor.execute(sql, params)
                return cursor.fetchall()
            except psycopg2.Error as e:
                handle_db_error(e, sql, params)
                return []

    def close(self):
        """关闭数据库连接"""
        if self._conn is None:
            return

        if self._conn.closed:
            return

        self._conn.close()
        self._conn = None

        logger.level3(msg=f'PostgreSQL connection to {self._db_args["dbname"]} closed')

    def __del__(self):
        self.close()


class AsyncPostgreSQLAdapter(AsyncDatabaseAdapter):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 5432, min_size: int = 10, max_size: int = 20, max_idle_time: int = 5 * 60 * 60,
            connect_timeout=5
    ):
        super().__init__()
        self.max_idle_time = float(max_idle_time)
        self._db_args = self._prepare_db_args(
            host, db, user, password, port, min_size, max_size, connect_timeout
        )
        self._lock = asyncio.Lock()
        self._pool = None
        self._last_use_time = time.time()

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(**config)

    def _prepare_db_args(
            self, host: str, db: str, user: Optional[str], password: Optional[str], port: int, min_size: int,
            max_size: int, connect_timeout: int
    ) -> dict:
        """准备数据库连接参数"""
        args = {
            'database': db,
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'min_size': min_size,
            'max_size': max_size,
            'command_timeout': connect_timeout
        }
        return args

    async def connect(self):
        """重新连接数据库"""
        try:
            self._pool = await asyncpg.create_pool(**self._db_args)
        except (ConnectionError, TimeoutError) as e:
            logger.level5(msg=f"PostgreSQL数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._last_use_time = time.time()

    @async_ensure_connected
    async def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> int:
        """执行sql语句"""
        async with self._pool.acquire() as conn:
            try:
                result = await conn.execute(sql, *params if params else ())
                affected_rows = int(result.split()[-1])
                return affected_rows if return_type == AdapterResultType.affected_rows else None
            except asyncpg.PostgresError as e:
                handle_db_error(e, sql, params)
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
            return 0

    @async_ensure_connected
    async def execute_many(self, sql: str, params: List[tuple], return_type=AdapterResultType.affected_rows) -> int:
        """执行多条sql语句"""
        async with self._pool.acquire() as conn:
            try:
                result = await conn.executemany(sql, params)
                affected_rows = sum(int(r.split()[-1]) for r in result)
                return affected_rows if return_type == AdapterResultType.affected_rows else None
            except asyncpg.PostgresError as e:
                handle_db_error(e, sql, params)
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
            return 0

    @async_ensure_connected
    async def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询并获取单个结果"""
        async with self._pool.acquire() as conn:
            try:
                return await conn.fetchrow(sql, *params if params else ())
            except asyncpg.PostgresError as e:
                handle_db_error(e, sql, params)
                return None

    @async_ensure_connected
    async def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        async with self._pool.acquire() as conn:
            try:
                return await conn.fetch(sql, *params if params else ())
            except asyncpg.PostgresError as e:
                handle_db_error(e, sql, params)
                return []

    async def close(self):
        """关闭数据库连接"""
        async with self._lock:
            if self._pool is None:
                return

            await self._pool.close()

            self._pool = None
            logger.level3(msg=f'PostgreSQL连接{self._db_args["database"]}数据库连接已关闭')
