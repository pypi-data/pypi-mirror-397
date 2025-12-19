import sqlite3
from functools import wraps
from typing import Any, List, Dict, Optional, Union
from pathlib import Path

import aiosqlite
from AioSpider import logger
from AioSpider.objects import AdapterResultType

from .adapter import DatabaseAdapter, AsyncDatabaseAdapter


def handle_db_error(e, sql: str, params):
    """处理数据库错误并打印信息"""
    error_type = type(e).__name__
    error_code = e.args[0]
    error_message = e.args[1]
    logger.level5(msg=f"SQLite {error_type}. 错误代码: {error_code}, 错误信息: {error_message}, SQL: {sql}, 参数: {params}")


def ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.connection is None:
            self.connect()
        return func(self, *args, **kwargs)

    return wrapper


def async_ensure_connected(func):
    """确保数据库连接有效，如果连接空闲时间过长则重新连接"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self._lock:
            if self.connection is None:
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


class SQLiteAdapter(DatabaseAdapter):

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "DatabaseAdapter":
        return cls(**config)

    def __init__(self, path: Union[str, Path], chunk_size: int = 1024 * 4, timeout: int = 10):
        self.path = str(path) if isinstance(path, Path) else path
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.connection = None

    def connect(self) -> None:
        self.connection = sqlite3.connect(database=self.path, timeout=self.timeout)
        self.connection.row_factory = sqlite3.Row

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                logger.level3(msg=f'sqlite连接{self.path}数据库连接已关闭')
            except sqlite3.ProgrammingError as e:
                pass
            self.connection = None

    @ensure_connected
    def execute(self, sql: str, params: Optional[Union[List, Dict]] = None, return_type=AdapterResultType.affected_rows) -> Any:
        cursor = self.connection.cursor()

        try:
            for statement in self._split_sql(sql):
                cursor.execute(statement, params or ())
            self.connection.commit()
            return return_data(self.connection, cursor, return_type, cursor.rowcount)
        except sqlite3.Error as e:
            handle_db_error(e, sql, params)
            self.connection.rollback()
        except Exception as e:
            logger.level5(msg=f"执行SQL失败: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
        return None

    @ensure_connected
    def execute_many(self, sql: str, params: Optional[Union[List, Dict]] = None, return_type=AdapterResultType.affected_rows) -> Any:
        cursor = self.connection.cursor()
        try:
            for statement in self._split_sql(sql):
                cursor.executemany(statement, params or ())
            self.connection.commit()
            return return_data(self.connection, cursor, return_type, cursor.rowcount)
        except sqlite3.IntegrityError as e:
            self.connection.rollback()
            if 'unique' in str(e).lower():
                logger.level5(msg=f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
            else:
                logger.level5(msg=f"IntegrityError: {e}")
        except Exception as e:
            self.connection.rollback()
            logger.level5(msg=f"执行多条SQL失败: {e}")
        finally:
            cursor.close()
        return None

    @ensure_connected
    def fetch_one(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Optional[Dict[str, Any]]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.level5(msg=f"获取单行失败: {e}")
        finally:
            cursor.close()
        return None

    @ensure_connected
    def fetch_all(self, sql: str, params: Optional[Union[List, Dict]] = None) -> List[Dict[str, Any]]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params or ())
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.level5(msg=f"获取所有行失败: {e}")
        finally:
            cursor.close()
        return []
    
    def __del__(self):
        self.close()

    @staticmethod
    def _split_sql(sql: str) -> List[str]:
        statements = []
        current_statement = []
        in_string = False
        string_delimiter = None
        
        for char in sql:
            if char in ["'", '"'] and not in_string:
                in_string = True
                string_delimiter = char
            elif char == string_delimiter and in_string:
                in_string = False
                string_delimiter = None
            
            current_statement.append(char)
            
            if char == ';' and not in_string:
                statements.append(''.join(current_statement).strip())
                current_statement = []
        
        if current_statement:
            statements.append(''.join(current_statement).strip())
        
        return [stmt for stmt in statements if stmt]
        

class AsyncSQLiteAdapter(AsyncDatabaseAdapter):

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "AsyncSQLiteAdapter":
        return cls(**config)

    def __init__(self, path: Union[str, Path], chunk_size: int = 1024 * 4, timeout: int = 10):
        self.path = str(path) if isinstance(path, Path) else path
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.connection = None

    async def connect(self) -> None:
        self.connection = await aiosqlite.connect(database=self.path, timeout=self.timeout, iter_chunk_size=self.chunk_size)
        self.connection.row_factory = aiosqlite.Row

    async def close(self):
        if self.connection:
            try:
                await self.connection.close()
                logger.level3(msg=f'sqlite连接{self.path}数据库连接已关闭')
            except sqlite3.ProgrammingError as e:
                pass
            self.connection = None

    @async_ensure_connected
    async def execute(self, sql: str, params: Optional[Union[List, Dict]] = None, return_type=AdapterResultType.affected_rows) -> Any:
        async with self.connection.cursor() as cur:
            try:
                await cur.execute(sql, params or ())
                await self.connection.commit()
                return return_data(self.connection, cur, return_type, cur.rowcount)
            except sqlite3.Error as e:
                handle_db_error(e, sql, params)
                await self.connection.rollback()
            except Exception as e:
                await self.connection.rollback()
                logger.level5(msg=f"执行SQL失败: {e}")
        return None

    @async_ensure_connected
    async def execute_many(self, sql: str, params: Optional[Union[List, Dict]] = None, return_type=AdapterResultType.affected_rows) -> Any:
        async with self.connection.cursor() as cur:
            try:
                await cur.executemany(sql, params or ())
                await self.connection.commit()
                return return_data(self.connection, cur, return_type, cur.rowcount)
            except sqlite3.Error as e:
                handle_db_error(e, sql, params)
                await self.connection.rollback()
            except Exception as e:
                logger.level5(msg=f"执行多条SQL失败: {e}")
                await self.connection.rollback()
        return None

    @async_ensure_connected
    async def fetch_one(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Optional[Dict[str, Any]]:
        async with self.connection.cursor() as cur:
            try:
                await cur.execute(sql, params or ())
                row = await cur.fetchone()
                return dict(row) if row else None
            except Exception as e:
                logger.level5(msg=f"获取单行失败: {e}")
        return None

    @async_ensure_connected
    async def fetch_all(self, sql: str, params: Optional[Union[List, Dict]] = None) -> List[Dict[str, Any]]:
        async with self.connection.cursor() as cur:
            try:
                await cur.execute(sql, params or ())
                return [dict(row) for row in await cur.fetchall()]
            except Exception as e:
                logger.level5(msg=f"获取所有行失败: {e}")
        return []
