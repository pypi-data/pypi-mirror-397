from abc import ABC, abstractmethod
from typing import Any, Tuple

from AioSpider.objects import DataBaseType

from .fields_conditions import Q, F
from .converst_value import convert_value

__all__ = ['UpdateBuilderFactory']


class AbstractUpdateBuilder(ABC):

    placeholder = '%s'

    def __init__(self, model):
        self.model = model
        self.table_name = self.model.Meta.table_name
        self.set_clauses = []
        self.where_conditions = []

    @abstractmethod
    def build_update_sql(self) -> Tuple[str, list]:
        pass

    def set(self, field: str, value: Any):
        self.set_clauses.append((field, convert_value(value)))
        return self

    def where(self, *conditions, **kwargs):
        for condition in conditions:
            if isinstance(condition, (Q, F)):
                self.where_conditions.append(condition)
        if kwargs:
            self.where_conditions.append(Q(**kwargs))
        return self

    def _build_where_clause(self):
        if not self.where_conditions:
            return "", []

        where_clauses = []
        values = []
        for condition in self.where_conditions:
            clause, params = condition.get_sql_and_params(self.placeholder)
            where_clauses.append(clause)
            values.extend(params)

        return " AND ".join(where_clauses), values

    def reset(self):
        self.set_clauses = []
        self.where_conditions = []


class MySQLUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        set_clause = ', '.join([f"`{field}` = {self.placeholder}" for field, _ in self.set_clauses])
        set_values = [value for _, value in self.set_clauses]

        sql = f"UPDATE `{self.table_name}` SET {set_clause}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, set_values + values


class SQLiteUpdateBuilder(AbstractUpdateBuilder):
    placeholder = '?'

    def build_update_sql(self) -> Tuple[str, list]:
        set_clause = ', '.join([f"`{field}` = {self.placeholder}" for field, _ in self.set_clauses])
        set_values = [value for _, value in self.set_clauses]

        sql = f"UPDATE `{self.table_name}` SET {set_clause}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, set_values + values


class OracleUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        set_clause = ', '.join([f"`{field}` = {self.placeholder}" for field, _ in self.set_clauses])
        set_values = [value for _, value in self.set_clauses]

        sql = f"UPDATE `{self.table_name}` SET {set_clause}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, set_values + values


class SQLServerUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        set_clause = ', '.join([f"`{field}` = {self.placeholder}" for field, _ in self.set_clauses])
        set_values = [value for _, value in self.set_clauses]

        sql = f"UPDATE `{self.table_name}` SET {set_clause}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, set_values + values


class PostgreSQLUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        set_clause = ', '.join([f"`{field}` = {self.placeholder}" for field, _ in self.set_clauses])
        set_values = [value for _, value in self.set_clauses]

        sql = f"UPDATE `{self.table_name}` SET {set_clause}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, set_values + values


class MariaDBUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        set_clause = ', '.join([f"`{field}` = {self.placeholder}" for field, _ in self.set_clauses])
        set_values = [value for _, value in self.set_clauses]

        sql = f"UPDATE `{self.table_name}` SET {set_clause}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, set_values + values


class MongoDBUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        # MongoDB does not use SQL for update operations
        return "MongoDB does not use SQL for update operations.", []


class RedisUpdateBuilder(AbstractUpdateBuilder):

    def build_update_sql(self) -> Tuple[str, list]:
        # Redis does not use SQL for update operations
        return "Redis does not use SQL for update operations.", []


class UpdateBuilderFactory:

    def __init__(self, model):
        self.model = model
        self.builder = self._select_builder()

    def _select_builder(self):
        db_type = self.model.Meta.database_type
        if db_type == DataBaseType.mysql:
            return MySQLUpdateBuilder(self.model)
        elif db_type == DataBaseType.sqlite:
            return SQLiteUpdateBuilder(self.model)
        elif db_type == DataBaseType.oracle:
            return OracleUpdateBuilder(self.model)
        elif db_type == DataBaseType.sqlserver:
            return SQLServerUpdateBuilder(self.model)
        elif db_type == DataBaseType.postgresql:
            return PostgreSQLUpdateBuilder(self.model)
        elif db_type == DataBaseType.mariadb:
            return MariaDBUpdateBuilder(self.model)
        elif db_type == DataBaseType.mongodb:
            return MongoDBUpdateBuilder(self.model)
        elif db_type == DataBaseType.redis:
            return RedisUpdateBuilder(self.model)
        elif db_type == DataBaseType.csv:
            pass
        elif db_type == DataBaseType.file:
            pass
        else:
            raise ValueError(f"不支持的数据库类型: {self.model.Meta.database_type}")

    def build(self):
        return self.builder.build_update_sql()

    def __getattr__(self, item):
        if hasattr(self.builder, item):
            return getattr(self.builder, item)
        raise AttributeError(f"'{self.__class__.__name__}' 没有 '{item}' 方法或属性")
