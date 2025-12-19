import re
import time
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Union, Any, List

import pymysql
from pymysql.converters import escape_string

from AioSpider import logger, tools
from AioSpider.db.sql import MysqlSelect, MysqlUpdate, MysqlInsert, MysqlDelete
from AioSpider.db.abc import SyncABC


class DescField:

    field: str = None
    type: str = None
    null: bool = None
    key: str = None
    length: Optional[int] = None
    default: Any = None
    extra: str = None

    def __init__(self, Field, Type, Null, Key, Default, Extra):
        self.field = Field

        length = tools.re_text(Type, r'\d+')
        self.length = self._convert_to_int(length)

        self.type = tools.re_sub(Type, r'\(\d+\)', '').upper()
        self.null = (Null == 'YES')
        self.key = Key
        self.default = Default
        self.extra = Extra

        if self.field in ['ID', 'Id']:
            self.field = 'id'

    @staticmethod
    def _convert_to_int(value):
        try:
            return int(value)
        except ValueError:
            return None

    @property
    def to_dict(self):
        return {
            'field': self.field, 'type': self.type, 'null': self.null, 'key': self.key,
            'length': self.length, 'default': self.default, 'extra': self.extra
        }

    def __str__(self):
        return str(self.to_dict)

    def __repr__(self):
        return str(self)


class SyncMySQLAPI(SyncABC):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, max_idle_time: int = 5 * 60 * 60, connect_timeout=5, time_zone: str = "+0:00",
            charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):
        
        super(SyncMySQLAPI, self).__init__()
        
        self.max_idle_time = float(max_idle_time)

        args = dict(
            use_unicode=True, charset=charset, database=db,
            init_command=f'SET time_zone = "{time_zone}"', sql_mode=sql_mode,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=connect_timeout
        )

        if user is not None:
            args["user"] = user

        if password is not None:
            args["passwd"] = password

        # 接受MySQL套接字文件的路径或 主机:端口 字符串
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = port

        if port:
            args['port'] = port

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except:
            logger.exception(f"Cannot connect to MySQL on {host}", exc_info=True)

    def __del__(self):
        """实例销毁后确保数据库连接关闭"""
        self.close()

    def reconnect(self):
        """重新连接数据库"""

        self._db = pymysql.connect(**self._db_args)
        self._db.autocommit(True)

    def _ensure_connected(self):
        """默认情况下，如果连接空闲时间过长（默认情况下为7小时），重新连接数据库"""

        if self._db is None or (time.time() - self._last_use_time > self.max_idle_time):
            self.reconnect()

        self._last_use_time = time.time()

    def _cursor(self):
        """创建游标"""
        self._ensure_connected()
        return self._db.cursor()

    def _make_table_sql(self, sql):
        table = tools.re(regx=r'table(.*?)\(', text=sql) or tools.re(regx=r'TABLE(.*?)\(', text=sql)
        return table[0].strip() if table else None

    def execute(self, sql: str) -> None:
        """执行sql语句"""

        self._ensure_connected()
        cursor = self._cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            self._db.rollback()
            logger.error(e)
        else:
            cursor.commit()
        finally:
            cursor.close()
            return cursor.lastrowid

    def _get(self, sql: str, *args, **kwargs) -> list:
        """查询一条数据"""

        cursor = self._cursor()
        try:
            cursor.execute(sql, kwargs or args)
            return cursor.fetchall()
        except Exception as e:
            logger.error(e)
            return []
        finally:
            cursor.close()

    def table_exist(self, table: str):
        """判断表是否存在"""

        tables = self.find(sql='show tables;')
        if table in [list(i.values())[0] for i in tables]:
            return True

        return False
    
    def create_table(
            self, table: Optional[str] = None, fields: Optional[dict] = None, sql: Optional[str] = None
    ):
        """
            创建表
            @params:
                table: 表名
                fields: 字段，如：fields={'name': 'TEXT'}
                sql: 原始sql语句，当sql参数不为None时，table、fields无效
        """

        if table is None and sql is not None:
            table = self._make_table_sql(sql)
        else:
            logger.debug(f'参数错误')
            return 

        if self.table_exist(table):
            logger.debug(f'{table} 表已存在')
            return

        sql = sql.replace('AUTOINCREMENT', 'AUTO_INCREMENT')

        self.execute(sql)
        logger.info(f'{table} 表自动创建成功')

    def desc(self, table: str) -> List[DescField]:

        result = self._get(f'desc {table}')
        return [DescField(**i) for i in result]

    def find(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            limit: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            sql: Optional[str] = None
    ):
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段约束
                limit: 数量
                group: 分组
                having: 筛选分组后的各组数据
                limit: 数量
                offset: 偏移量
                order: 排序约束
                desc: 是否倒序
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = str(MysqlSelect(
                table=table, field=field, limit=limit, offset=offset, desc=desc, order=order,
                where=where, group=group, having=having
            ))

        return self._get(sql)

    def insert(self, table: str, items: list, sql: Optional[str] = None, auto_update: bool = False):
        """
            插入或更新多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
                sql: 原始sql语句，当sql参数不为None时，table、items无效
        """

        if sql is None:

            if not items:
                return

            if isinstance(items, dict):
                items = [items]

            field = list(items[0].keys())
            values = [list(i.values()) for i in items]
            sql = str(MysqlInsert(table, field, values, auto_update=auto_update))

        self.execute(sql)

    def update(self, table: str, item: dict, where: dict = None):
        """
            更新多条数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
                wheres: 更新条件
        """

        if not item:
            return

        sql = str(MysqlUpdate(table, item, where))

        self.execute(sql)

    def delete(self, table: str, where: dict, sql: str = None) -> None:
        """
            更新一条数据
            @params:
                table: 表名
                item: 需要修改的数据，dict -> {'a': 1, 'b': 2}
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、item、where无效
        """

        if sql is None:
            sql = str(MysqlDelete(table=table, where=where))

        self.execute(sql)
            
    def close(self):
        """关闭数据库连接"""

        if self._db is None:
            return 
        
        self._db.close()
        self._db = None
        logger.info(f'mysql连接{self._db_args["database"]}数据库连接已关闭')
            