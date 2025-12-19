from abc import ABC, abstractmethod

from AioSpider.objects import DataBaseType

from .fields_conditions import Q

__all__ = ['DeleteBuilderFactory']


class AbstractDeleteBuilder(ABC):
    placeholder = '%s'

    def __init__(self, model):
        self.model = model
        self.table_name = self.model.Meta.table_name
        self.where_conditions = []

    @abstractmethod
    def build_delete_sql(self) -> str:
        pass

    def where(self, *conditions, **kwargs):
        for condition in conditions:
            if isinstance(condition, Q):
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
        self.where_conditions = []


class MySQLDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        sql = f"DELETE FROM {self.table_name}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, values


class SQLiteDeleteBuilder(AbstractDeleteBuilder):
    placeholder = '?'

    def build_delete_sql(self) -> str:
        sql = f"DELETE FROM {self.table_name}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, values


class OracleDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        sql = f"DELETE FROM {self.table_name}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, values


class SQLServerDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        sql = f"DELETE FROM {self.table_name}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, values


class PostgreSQLDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        sql = f"DELETE FROM {self.table_name}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, values


class MariaDBDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        sql = f"DELETE FROM {self.table_name}"

        where_clause, values = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"

        return sql, values


class MongoDBDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        # MongoDB does not use SQL for delete operations
        return "MongoDB does not use SQL for delete operations."


class RedisDeleteBuilder(AbstractDeleteBuilder):

    def build_delete_sql(self) -> str:
        # Redis does not use SQL for delete operations
        return "Redis does not use SQL for delete operations."


class DeleteBuilderFactory:

    def __init__(self, model):
        self.model = model
        self.builder = self._select_builder()

    def _select_builder(self):
        db_type = self.model.Meta.database_type
        if db_type == DataBaseType.mysql:
            return MySQLDeleteBuilder(self.model)
        elif db_type == DataBaseType.sqlite:
            return SQLiteDeleteBuilder(self.model)
        elif db_type == DataBaseType.oracle:
            return OracleDeleteBuilder(self.model)
        elif db_type == DataBaseType.mysql.sqlserver:
            return SQLServerDeleteBuilder(self.model)
        elif db_type == DataBaseType.mysql.postgresql:
            return PostgreSQLDeleteBuilder(self.model)
        elif db_type == DataBaseType.mysql.mariadb:
            return MariaDBDeleteBuilder(self.model)
        elif db_type == DataBaseType.mongodb:
            return MongoDBDeleteBuilder(self.model)
        elif db_type == DataBaseType.redis:
            return RedisDeleteBuilder(self.model)
        elif db_type == DataBaseType.csv:
            pass
        elif db_type == DataBaseType.file:
            pass
        else:
            raise ValueError(f"不支持的数据库类型: {self.model.Meta.database_type}")

    def build(self):
        return self.builder.build_delete_sql()

    def __getattr__(self, item):
        if hasattr(self.builder, item):
            return getattr(self.builder, item)
        raise AttributeError(f"'{self.__class__.__name__}' 没有 '{item}' 方法或属性")
