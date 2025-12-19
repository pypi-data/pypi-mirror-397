import datetime
from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, Any

from AioSpider.objects import DataBaseType
from .converst_value import convert_value

__all__ = ['InsertBuilderFactory']


class AbstractInsertBuilder(ABC):
    placeholder = '%s'

    def __init__(self, model):
        self.table_name = model.Meta.table_name
        self.columns = []
        self.values = []
        self.on_duplicate_key_updates = {}

    @abstractmethod
    def build_insert_sql(self) -> str:
        pass

    def add_column(self, column: str):
        if column not in self.columns:
            self.columns.append(column)
        return self

    def add_row(self, row: Dict[str, Any]):
        for column in row:
            self.add_column(column)
        self.values.append(tuple(convert_value(v) for v in row.values()))
        return self

    def on_duplicate_key_update(self, row: Dict[str, Any]):
        self.on_duplicate_key_updates.update(row)
        return self

    def reset(self):
        self.columns = []
        self.values = []
        self.on_duplicate_key_updates = {}


class MySQLInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        placeholders = ', '.join([self.placeholder] * len(self.columns))
        columns = ', '.join([f"`{col}`" for col in self.columns])
        sql = f"INSERT INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"

        if self.on_duplicate_key_updates:
            update_stmt = ', '.join([f"`{col}` = VALUES(`{col}`)" for col in self.on_duplicate_key_updates])
            sql += f" ON DUPLICATE KEY UPDATE {update_stmt}"

        return sql, self.values


class SQLiteInsertBuilder(AbstractInsertBuilder):
    placeholder = '?'

    def build_insert_sql(self):
        placeholders = ', '.join([self.placeholder] * len(self.columns))
        columns = ', '.join(self.columns)

        if self.on_duplicate_key_updates:
            sql = f"INSERT OR REPLACE INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"
        else:
            sql = f"INSERT INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"

        return sql, self.values


class OracleInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        placeholders = ', '.join([':' + str(i + 1) for i in range(len(self.columns))])
        columns = ', '.join(self.columns)
        sql = f"INSERT INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"

        if self.on_duplicate_key_updates:
            update_stmt = ', '.join([f"{col} = :{col}" for col in self.on_duplicate_key_updates])
            sql += f" ON DUPLICATE KEY UPDATE {update_stmt}"

        return sql, self.values


class SQLServerInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        placeholders = ', '.join(['@' + col for col in self.columns])
        columns = ', '.join(self.columns)
        sql = f"INSERT INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"

        if self.on_duplicate_key_updates:
            update_stmt = ', '.join([f"{col} = @{col}" for col in self.on_duplicate_key_updates])
            sql += f" ON DUPLICATE KEY UPDATE {update_stmt}"

        return sql, self.values


class PostgreSQLInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        placeholders = ', '.join([self.placeholder] * len(self.columns))
        columns = ', '.join(self.columns)
        sql = f"INSERT INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"

        if self.on_duplicate_key_updates:
            update_stmt = ', '.join([f"{col} = EXCLUDED.{col}" for col in self.on_duplicate_key_updates])
            sql += f" ON CONFLICT DO UPDATE SET {update_stmt}"

        return sql, self.values


class MariaDBInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        placeholders = ', '.join([self.placeholder] * len(self.columns))
        columns = ', '.join([f"`{col}`" for col in self.columns])
        sql = f"INSERT INTO `{self.table_name}` ({columns}) VALUES ({placeholders})"

        if self.on_duplicate_key_updates:
            update_stmt = ', '.join([f"{col} = VALUES({col})" for col in self.on_duplicate_key_updates])
            sql += f" ON DUPLICATE KEY UPDATE {update_stmt}"

        return sql, self.values


class MongoDBInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        # MongoDB does not use SQL for insert operations
        return "MongoDB does not use SQL for insert operations."


class RedisInsertBuilder(AbstractInsertBuilder):

    def build_insert_sql(self):
        # Redis does not use SQL for insert operations
        return "Redis does not use SQL for insert operations."


class InsertBuilderFactory:

    def __init__(self, model):
        self.model = model
        self.builder = self._select_builder()

    def _select_builder(self):
        db_type = self.model.Meta.database_type
        if db_type == DataBaseType.mysql:
            return MySQLInsertBuilder(self.model)
        elif db_type == DataBaseType.sqlite:
            return SQLiteInsertBuilder(self.model)
        elif db_type == DataBaseType.oracle:
            return OracleInsertBuilder(self.model)
        elif db_type == DataBaseType.sqlserver:
            return SQLServerInsertBuilder(self.model)
        elif db_type == DataBaseType.postgresql:
            return PostgreSQLInsertBuilder(self.model)
        elif db_type == DataBaseType.mariadb:
            return MariaDBInsertBuilder(self.model)
        elif db_type == DataBaseType.mongodb:
            return MongoDBInsertBuilder(self.model)
        elif db_type == DataBaseType.redis:
            return RedisInsertBuilder(self.model)
        elif db_type == DataBaseType.csv:
            pass
        elif db_type == DataBaseType.file:
            pass
        else:
            raise ValueError(f"不支持的数据库类型: {self.model.Meta.database_type}")

    def build(self):
        return self.builder.build_insert_sql()

    def __getattr__(self, item):
        if hasattr(self.builder, item):
            return getattr(self.builder, item)
        raise AttributeError(f"'{self.__class__.__name__}' 没有 '{item}' 方法或属性")
