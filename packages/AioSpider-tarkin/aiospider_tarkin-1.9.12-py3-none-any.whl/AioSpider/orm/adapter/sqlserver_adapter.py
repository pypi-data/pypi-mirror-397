import asyncio
import time
from typing import Any, Optional, List, Dict
from functools import wraps

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    pyodbc = None

try:
    import aioodbc
    AIOODBC_AVAILABLE = True
except ImportError:
    AIOODBC_AVAILABLE = False
    aioodbc = None

from AioSpider import logger
from AioSpider.objects import AdapterResultType

from .adapter import DatabaseAdapter, AsyncDatabaseAdapter

__all__ = ['SQLServerAdapter', 'AsyncSQLServerAdapter']


def handle_db_error(e, sql: str, params):
    """处理数据库错误并打印信息"""
    error_type = type(e).__name__
    error_code = e.args[0]
    error_message = e.args[1]
    logger.level5(msg=f"SQLServer {error_type}. 错误代码: {error_code}, 错误信息: {error_message}, SQL: {sql}, 参数: {params}")


def ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._conn is None or (time.time() - self._last_use_time > self.max_idle_time):
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


class SQLServerAdapter(DatabaseAdapter):
    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 1433, max_idle_time: int = 5 * 60 * 60, connect_timeout=5
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
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={db};UID={user};PWD={password};CONNECTION TIMEOUT={connect_timeout}'

    def connect(self):
        """重新连接数据库"""
        try:
            self._conn = pyodbc.connect(self._db_args)
        except (ConnectionError, TimeoutError) as e:
            logger.level5(msg=f"SQLServer数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._conn.autocommit = True
        self._last_use_time = time.time()

    @ensure_connected
    def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> Dict[str, Any]:
        """执行sql语句"""
        with self._conn.cursor() as cursor:
            try:
                affected_rows = cursor.execute(sql, params).rowcount
                self._conn.commit()
                return return_data(cursor, return_type, affected_rows)
            except pyodbc.Error as e:
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
                affected_rows = cursor.executemany(sql, params).rowcount
                self._conn.commit()
                return return_data(cursor, return_type, affected_rows)
            except pyodbc.Error as e:
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
                cursor.execute(sql, params)
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
            except pyodbc.Error as e:
                handle_db_error(e, sql, params)
                return None

    @ensure_connected
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            except pyodbc.Error as e:
                handle_db_error(e, sql, params)
                return []

    def close(self):
        """关闭数据库连接"""
        if self._conn is None:
            return

        self._conn.close()
        self._conn = None

        logger.level3(msg=f'SQLServer connection closed')

    def __del__(self):
        self.close()


class AsyncSQLServerAdapter(AsyncDatabaseAdapter):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 1433, min_size: int = 10, max_size: int = 20, max_idle_time: int = 5 * 60 * 60,
            connect_timeout=5
    ):
        super().__init__()
        self.max_idle_time = float(max_idle_time)
        self._db_args = self._prepare_db_args(
            host, db, user, password, port, connect_timeout
        )
        self._pool_args = {
            'minsize': min_size,
            'maxsize': max_size,
            'loop': asyncio.get_event_loop()
        }
        self._lock = asyncio.Lock()
        self._pool = None
        self._last_use_time = time.time()

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(**config)

    def _prepare_db_args(self, host: str, db: str, user: Optional[str], password: Optional[str], port: int, connect_timeout: int) -> str:
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={db};UID={user};PWD={password};CONNECTION TIMEOUT={connect_timeout}'

    async def connect(self):
        """重新连接数据库"""
        try:
            self._pool = await aioodbc.create_pool(dsn=self._db_args, **self._pool_args)
        except (ConnectionError, TimeoutError) as e:
            logger.level5(msg=f"SQLServer数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._last_use_time = time.time()

    @async_ensure_connected
    async def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> int:
        """执行sql语句"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    affected_rows = await cursor.execute(sql, params)
                    await conn.commit()
                    return return_data(cursor, return_type, affected_rows)
                except pyodbc.Error as e:
                    handle_db_error(e, sql, params)
                    await conn.rollback()
                except Exception as e:
                    logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
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
                except pyodbc.Error as e:
                    handle_db_error(e, sql, params)
                    await conn.rollback()
                except Exception as e:
                    logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
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
                    await cursor.execute(sql, params)
                    columns = [column[0] for column in cursor.description]
                    row = await cursor.fetchone()
                    return dict(zip(columns, row)) if row else None
                except pyodbc.Error as e:
                    handle_db_error(e, sql, params)
                    return None

    @async_ensure_connected
    async def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(sql, params)
                    columns = [column[0] for column in cursor.description]
                    rows = await cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                except pyodbc.Error as e:
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
            logger.level3(msg=f'SQLServer连接池已关闭')
