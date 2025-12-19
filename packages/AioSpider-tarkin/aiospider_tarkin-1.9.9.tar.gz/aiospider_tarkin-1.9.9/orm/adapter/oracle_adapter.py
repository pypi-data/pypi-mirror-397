import asyncio
import time
from typing import Any, Optional, List, Dict
from functools import wraps

try:
    import cx_Oracle
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    cx_Oracle = None

try:
    import aioodbc
    AIOODBC_AVAILABLE = True
except ImportError:
    AIOODBC_AVAILABLE = False
    aioodbc = None

from AioSpider import logger
from AioSpider.objects import AdapterResultType

from .adapter import DatabaseAdapter, AsyncDatabaseAdapter

__all__ = ['OracleAdapter', 'AsyncOracleAdapter']


def handle_db_error(e, sql: str, params):
    """处理数据库错误并打印信息"""
    error_type = type(e).__name__
    error_code = e.code
    error_message = str(e)
    logger.level5(msg=f"Oracle {error_type}. 错误代码: {error_code}, 错误信息: {error_message}, SQL: {sql}, 参数: {params}")


def ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._conn is None or not self._conn.ping() or (time.time() - self._last_use_time > self.max_idle_time):
            self.connect()
        return func(self, *args, **kwargs)

    return wrapper


def async_ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self._lock:
            if self._pool is None or (time.time() - self._last_use_time > self.max_idle_time):
                await self.connect()
        return await func(self, *args, **kwargs)

    return wrapper


def return_data(cursor, return_type, affected_rows):
    """根据返回类型返回数据"""
    if return_type == AdapterResultType.lastrowid:
        return cursor.lastrowid
    elif return_type == AdapterResultType.affected_rows:
        return affected_rows
    elif return_type == AdapterResultType.rowcount:
        return cursor.rowcount
    else:
        return None


class OracleAdapter(DatabaseAdapter):
    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 1521, max_idle_time: int = 5 * 60 * 60, connect_timeout=5
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
        dsn = cx_Oracle.makedsn(host, port, service_name=db)
        return {
            'user': user,
            'password': password,
            'dsn': dsn,
            'encoding': 'UTF-8',
            'nencoding': 'UTF-8',
            'timeout': connect_timeout
        }

    def connect(self):
        """重新连接数据库"""
        try:
            self._conn = cx_Oracle.connect(**self._db_args)
        except cx_Oracle.Error as e:
            logger.level5(msg=f"Oracle数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._last_use_time = time.time()

    @ensure_connected
    def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> Dict[str, Any]:
        """执行sql语句"""
        with self._conn.cursor() as cursor:
            try:
                affected_rows = cursor.execute(sql, params or ())
                self._conn.commit()
                return return_data(cursor, return_type, affected_rows)
            except cx_Oracle.Error as e:
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
        with self._conn.cursor() as cursor:
            try:
                affected_rows = cursor.executemany(sql, params)
                self._conn.commit()
                return return_data(cursor, return_type, affected_rows)
            except cx_Oracle.Error as e:
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
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sql, params or ())
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
            except cx_Oracle.Error as e:
                handle_db_error(e, sql, params)
                return None

    @ensure_connected
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sql, params or ())
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            except cx_Oracle.Error as e:
                handle_db_error(e, sql, params)
                return []

    def close(self):
        """关闭数据库连接"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.level3(msg=f'Oracle connection to {self._db_args["dsn"]} closed')

    def __del__(self):
        self.close()


class AsyncOracleAdapter(AsyncDatabaseAdapter):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 1521, min_size: int = 10, max_size: int = 20, max_idle_time: int = 5 * 60 * 60,
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
        dsn = cx_Oracle.makedsn(host, port, service_name=db)
        connection_string = f'Driver={{Oracle}};DBQ={dsn};UID={user};PWD={password}'
        return {
            'dsn': connection_string,
            'minsize': min_size,
            'maxsize': max_size,
            'timeout': connect_timeout,
            'autocommit': True,
            'loop': asyncio.get_event_loop()
        }

    async def connect(self):
        """重新连接数据库"""
        try:
            self._pool = await aioodbc.create_pool(**self._db_args)
        except Exception as e:
            logger.level5(msg=f"Oracle数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._last_use_time = time.time()

    @async_ensure_connected
    async def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> int:
        """执行sql语句"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    affected_rows = await cursor.execute(sql, params or ())
                    await conn.commit()
                    return return_data(cursor, return_type, affected_rows)
                except Exception as e:
                    handle_db_error(e, sql, params)
                    await conn.rollback()
                finally:
                    await conn.rollback()
                    return 0

    @async_ensure_connected
    async def execute_many(self, sql: str, params: List[tuple], return_type=AdapterResultType.affected_rows) -> int:
        """执行多条sql语句"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:    
                    affected_rows = await cursor.executemany(sql, params)
                    await conn.commit()
                    return return_data(cursor, return_type, affected_rows)
                except Exception as e:
                    handle_db_error(e, sql, params)
                    await conn.rollback()
                finally:
                    await conn.rollback()
                    return 0

    @async_ensure_connected
    async def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询并获取单个结果"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(sql, params or ())
                    columns = [column[0] for column in cursor.description]
                    row = await cursor.fetchone()
                    return dict(zip(columns, row)) if row else None
                except Exception as e:
                    handle_db_error(e, sql, params)
                    return None

    @async_ensure_connected
    async def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(sql, params or ())
                    columns = [column[0] for column in cursor.description]
                    rows = await cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                except Exception as e:
                    handle_db_error(e, sql, params)
                    return []

    async def close(self):
        """关闭数据库连接"""
        async with self._lock:
            if self._pool is None:
                return

            self._pool.close()
            await self._pool.wait_closed()

            self._pool = None
            logger.level3(msg=f'Oracle连接{self._db_args["dsn"]}数据库连接已关闭')
