import asyncio
import time
from tkinter.messagebox import RETRY
from typing import Any, Optional, List, Dict
from functools import wraps

import pymysql
import aiomysql
from pymysql.cursors import DictCursor

from AioSpider import logger
from AioSpider.objects import AdapterResultType

from .adapter import DatabaseAdapter, AsyncDatabaseAdapter

__all__ = ['MySQLAdapter', 'AsyncMySQLAdapter']



def handle_db_error(e, sql: str, params):
    """处理数据库错误并打印信息"""
    error_type = type(e).__name__
    error_code = e.args[0]
    error_message = e.args[1]
    logger.level5(msg=f"MySQL {error_type}. 错误代码: {error_code}, 错误信息: {error_message}, SQL: {sql}, 参数: {params}")


def ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        need_reconnect = False

        # 检查连接是否存在
        if self._conn is None:
            need_reconnect = True
        else:
            try:
                # 测试连接是否有效
                cursor = self._conn.cursor()
                cursor.execute('SELECT 1')
            except Exception as e:
                logger.error(f"数据库连接测试失败: {str(e)}")
                need_reconnect = True

            # 检查空闲时间
            if time.time() - self._last_use_time > self.max_idle_time:
                need_reconnect = True

        if need_reconnect:
            # 关闭旧连接
            if self._conn is not None:
                self._conn.close()
            # 创建新连接
            self.connect()

        return func(self, *args, **kwargs)

    return wrapper


def async_ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self._lock:
            need_reconnect = False

            # 检查连接池是否存在
            if self._pool is None:
                need_reconnect = True
            else:
                try:
                    # 获取一个连接进行测试
                    async with self._pool.acquire() as conn:
                        async with conn.cursor() as cursor:
                            await cursor.execute('SELECT 1')
                except Exception as e:
                    logger.error(f"数据库连接测试失败: {str(e)}")
                    need_reconnect = True

                # 检查空闲时间
                if time.time() - self._last_use_time > self.max_idle_time:
                    need_reconnect = True

            if need_reconnect:
                # 关闭旧连接池
                if self._pool is not None:
                    self._pool.close()
                    await self._pool.wait_closed()
                # 创建新连接池
                await self.connect()

        return await func(self, *args, **kwargs)

    return wrapper


def return_data(conn, cursor, return_type, affected_rows):
    """根据返回类型返回数据"""
    if return_type == AdapterResultType.lastrowid:
        return cursor.lastrowid
    elif return_type == AdapterResultType.affected_rows:
        return affected_rows
    elif return_type == AdapterResultType.rowcount:
        return cursor.rowcount
    elif return_type == AdapterResultType.insertid:
        return conn.insert_id()
    else:
        return None


class MySQLAdapter(DatabaseAdapter):
    """MySQL数据库适配器"""

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, max_idle_time: int = 5 * 60 * 60, connect_timeout=5, time_zone: str = "+0:00",
            charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):
        super().__init__()
        self.max_idle_time = float(max_idle_time)
        self._db_args = self._prepare_db_args(
            host, db, user, password, port, connect_timeout, time_zone, charset, sql_mode
        )
        self._conn = None
        self._last_use_time = time.time()

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(**config)

    def _prepare_db_args(self, host, db, user, password, port, connect_timeout, time_zone, charset, sql_mode):
        args = {
            'database': db,
            'user': user,
            'password': password,
            'charset': charset,
            'use_unicode': True,
            'init_command': f'SET time_zone = "{time_zone}"',
            'sql_mode': sql_mode,
            'cursorclass': DictCursor,
            'connect_timeout': connect_timeout
        }
        if '/' in host:
            args['unix_socket'] = host
        else:
            host, port = self._parse_host_port(host, port)
            args['host'] = host
            args['port'] = port
        return args

    @staticmethod
    def _parse_host_port(host, port):
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        return host, port

    def connect(self):
        """重新连接数据库"""
        try:
            self._conn = pymysql.connect(**self._db_args)
        except (ConnectionError, TimeoutError) as e:
            logger.level5(msg=f"MySQL数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
            raise e
        self._conn.autocommit(True)
        self._last_use_time = time.time()

    @ensure_connected
    def execute(self, sql: str, params: Optional[tuple] = None, return_type=AdapterResultType.affected_rows) -> Dict[str, Any]:
        """执行sql语句"""
        with self._conn.cursor() as cursor:
            try:
                affected_rows = cursor.execute(sql, params)
                self._conn.commit()
                return return_data(self._conn, cursor, return_type, affected_rows)
            except aiomysql.Error as e:
                handle_db_error(e, sql, params)
                self._conn.rollback()
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
                self._conn.rollback()
            return 0

    @ensure_connected
    def execute_many(self, sql: str, params: List[tuple], return_type=AdapterResultType.affected_rows) -> int:
        """执行多条sql语句"""
        with self._conn.cursor() as cursor:
            try:
                affected_rows = cursor.executemany(sql, params)
                self._conn.commit()
                return return_data(self._conn, cursor, return_type, affected_rows)
            except aiomysql.Error as e:
                handle_db_error(e, sql, params)
                self._conn.rollback()
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
                self._conn.rollback()
            return 0

    @ensure_connected
    def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询并获取单个结果"""
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                return cursor.fetchone()
            except pymysql.Error as e:
                handle_db_error(e, sql, params)
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
        return None

    @ensure_connected
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                return cursor.fetchall()
            except pymysql.Error as e:
                handle_db_error(e, sql, params)
            except Exception as e:
                logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
        return []


    def close(self):
        """关闭数据库连接"""
        if self._conn is None:
            return

        if self._conn._closed:
            return

        self._conn.close()
        self._conn = None

        logger.level3(msg=f'MySQL connection to {self._db_args["database"]} closed')

    def __del__(self):
        self.close()


class AsyncMySQLAdapter(AsyncDatabaseAdapter):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, min_size: int = 10, max_size: int = 20, max_idle_time: int = 5 * 60 * 60,
            connect_timeout=5, time_zone: str = "+0:00", charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):
        super().__init__()
        self.max_idle_time = float(max_idle_time)
        self._db_args = self._prepare_db_args(
            host, db, user, password, port, min_size, max_size, connect_timeout,
            time_zone, charset, sql_mode
        )
        self._lock = asyncio.Lock()
        self._pool = None
        self._last_use_time = time.time()

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(**config)

    def _prepare_db_args(
            self, host: str, db: str, user: Optional[str], password: Optional[str], port: int, min_size: int,
            max_size: int, connect_timeout: int, time_zone: str, charset: str, sql_mode: str
    ) -> dict:
        """准备数据库连接参数"""
        args = {
            'use_unicode': True,
            'charset': charset,
            'db': db,
            'minsize': min_size,
            'maxsize': max_size,
            'init_command': f'SET time_zone = "{time_zone}"',
            'sql_mode': sql_mode,
            'cursorclass': aiomysql.cursors.DictCursor,
            'connect_timeout': connect_timeout,
            'autocommit': True,
            'loop': asyncio.get_event_loop()
        }

        if user:
            args["user"] = user
        if password:
            args["password"] = password

        if "/" in host:
            args["unix_socket"] = host
        else:
            host_parts = host.split(":")
            args["host"] = host_parts[0]
            args["port"] = int(host_parts[1]) if len(host_parts) == 2 else port

        return args

    async def connect(self):
        """重新连接数据库"""
        try:
            self._pool = await aiomysql.create_pool(**self._db_args)
        except (ConnectionError, TimeoutError) as e:
            logger.level5(msg=f"MySQL数据库连接失败, 参数: {self._db_args}, 错误信息: {e}")
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
                    return return_data(conn, cursor, return_type, affected_rows)
                except aiomysql.Error as e:
                    handle_db_error(e, sql, params)
                    await conn.rollback()
                except Exception as e:
                    logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
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
                    return return_data(conn, cursor, return_type, affected_rows)
                except aiomysql.Error as e:
                    handle_db_error(e, sql, params)
                    await conn.rollback()
                except Exception as e:
                    logger.level5(msg=f"意外的SQL执行错误: {e}, SQL: {sql}, 参数: {params}")
                    await conn.rollback()
                return 0

    @async_ensure_connected
    async def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询并获取单个结果"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(sql, params)
                    return await cursor.fetchone()
                except aiomysql.Error as e:
                    handle_db_error(e, sql, params)
                    return None

    @async_ensure_connected
    async def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并获取所有结果"""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(sql, params)
                    return await cursor.fetchall()
                except aiomysql.Error as e:
                    handle_db_error(e, sql, params)
                    return []

    async def close(self):
        """关闭数据库连接"""

        async with self._lock:
            if self._pool is None:
                return

            if self._pool._closed:
                return

            self._pool.close()
            await self._pool.wait_closed()

            self._pool = None
            logger.level3(msg=f'mysql连接{self._db_args["db"]}数据库连接已关闭')
