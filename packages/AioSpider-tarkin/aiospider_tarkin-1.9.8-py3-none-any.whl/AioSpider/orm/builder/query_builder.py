from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

from AioSpider.objects import DataBaseType

from .joins import Join
from .fields_conditions import Q, F
from .aggregates import Aggregate

__all__ = ['QueryBuilderFactory']


class AbstractQueryBuilder(ABC):
    placeholder = '%s'

    def __init__(self, model):
        self.model = model
        self.table_name = model.table_name
        self.fields = []
        self.where_conditions = []
        self.order_by_clauses = []
        self.limit = None
        self.offset = None
        self.group_by_fields = []
        self.having_conditions = []
        self.joins = []
        self.values = []

    def optimize_query(self):
        """实现查询优化逻辑"""

        # 1. 优化选择的字段
        if not self.fields or self.fields == ["*"]:
            self.fields = [f"`{field.column}`" for field in self.model.fields.values()]
        
        # 3. 优化JOIN
        self.joins = [join for join in self.joins if join.is_necessary()]
        
        # 4. 优化ORDER BY
        if self.limit is not None and not self.order_by_clauses:
            primary_key = self.model.get_primary_key()
            if primary_key:
                self.order_by_clauses.extend([(key, "ASC") for key in primary_key])
        
        # 5. 优化LIMIT和OFFSET
        if self.offset is not None and self.limit is None:
            self.limit = 2**63 - 1      # 设置一个很大的限制
        
        # 6. 优化GROUP BY
        if self.group_by_fields:
            self.group_by_fields = list(set(self.group_by_fields))  # 去重
        
        # 7. 优化HAVING
        if not self.group_by_fields:
            self.having_conditions = {}

    @abstractmethod
    def build_query_sql(self) -> Tuple[str, list]:
        pass

    def select(self, *fields):
        for field in fields:
            if isinstance(field, str):
                self.fields.append(f'`{field}`')
            else:
                self.fields.append(str(field))
        if not self.fields:
            self.fields = ["*"]
        return self

    def defer(self, *fields):
        for field in fields:
            self.fields.remove(f"`{field}`")
        if not self.fields:
            self.fields = [f'`{field.column}`' for field in self.model.fields.values() if field.column not in fields]
        return self
    
    def exclude(self, **kwargs):
        self.where(**{f'{field}__ne': value for field, value in kwargs.items()})
        return self

    def order_by(self, *fields):
        for field in fields:
            if field.startswith('-'):
                self.order_by_clauses.append((field.strip('-'), "DESC"))
            else:
                self.order_by_clauses.append((field, "ASC"))
        return self

    def join(self, table: str, condition: str, join_type: str = 'INNER'):
        self.joins.append(Join(table, condition, join_type))
        return self

    def left_join(self, table: str, condition: str):
        return self.join(table, condition, 'LEFT')

    def right_join(self, table: str, condition: str):
        return self.join(table, condition, 'RIGHT')

    def outer_join(self, table: str, condition: str):
        return self.join(table, condition, 'FULL OUTER')

    def where(self, *conditions, **kwargs):
        for condition in conditions:
            if isinstance(condition, (Q, F)):
                self.where_conditions.append(condition)
        if kwargs:
            self.where_conditions.append(Q(**kwargs))
        return self

    def limit_offset(self, limit: int, offset: int = 0):
        self.limit = limit
        self.offset = offset
        return self

    def group_by(self, *fields: str):
        self.group_by_fields.extend(fields)
        return self

    def having(self, *conditions, **kwargs):
        for condition in conditions:
            if isinstance(condition, (Q, F)):
                self.having_conditions.append(condition)
        if kwargs:
            self.having_conditions.append(Q(**kwargs))
        return self

    def count(self, field: str = "*"):
        self.fields = [f"COUNT({field}) AS count_{field}"]
        return self

    def max(self, field: str):
        self.fields = [f"MAX({field}) AS max_{field}"]
        return self

    def min(self, field: str):
        self.fields = [f"MIN({field}) AS min_{field}"]
        return self

    def avg(self, field: str):
        self.fields = [f"AVG({field}) AS avg_{field}"]
        return self

    def sum(self, field: str):
        self.fields = [f"SUM({field}) AS sum_{field}"]
        return self

    def subquery(self, subquery: 'AbstractQueryBuilder', alias: str):
        self.fields.append(f"({subquery.build_query_sql()}) AS {alias}")
        return self

    def annotate(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, Aggregate):
                self.fields.append(f"{value} AS {key}")
        return self

    def _build_where_clause(self):
        if not self.where_conditions:
            return "", []

        where_clauses = []
        where_params = []
        for condition in self.where_conditions:
            clause, params = condition.get_sql_and_params(self.placeholder)
            where_clauses.append(clause)
            where_params.extend(params)

        return " AND ".join(where_clauses), where_params

    def _build_having_clause(self):
        if not self.having_conditions:
            return "", []

        having_clauses = []
        having_params = []
        for condition in self.having_conditions:
            clause, params = condition.get_sql_and_params(self.placeholder)
            having_clauses.append(clause)
            having_params.extend(params)

        return " AND ".join(having_clauses), having_params

    def reset(self):
        self.fields = []
        self.where_conditions = []
        self.order_by_clauses = []
        self.limit = None
        self.offset = None
        self.group_by_fields = []
        self.having_conditions = []
        self.joins = []
        self.values = []


class MySQLQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> Tuple[str, list]:
        self.optimize_query()
        sql = f"SELECT {', '.join(self.fields)} FROM `{self.table_name}`"

        for join in self.joins:
            sql += f" {join}"

        where_clause, where_params = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"
        self.values.extend(where_params)

        if self.group_by_fields:
            sql += f" GROUP BY {', '.join(self.group_by_fields)}"

        having_clauses, having_params = self._build_having_clause()
        if having_clauses:
            sql += f" HAVING {having_clauses}"
        self.values.extend(having_params)

        if self.order_by_clauses:
            order_clauses = [f"`{field}` {order}" for field, order in self.order_by_clauses]
            sql += f" ORDER BY {', '.join(order_clauses)}"

        if self.limit is not None:
            sql += f" LIMIT {self.limit}"

        if self.offset is not None:
            sql += f" OFFSET {self.offset}"

        return sql, self.values


class SQLiteQueryBuilder(AbstractQueryBuilder):
    placeholder = '?'

    def build_query_sql(self) -> Tuple[str, list]:
        self.optimize_query()
        sql = f"SELECT {', '.join(self.fields)} FROM `{self.table_name}`"

        for join in self.joins:
            sql += f" {join}"

        where_clause, where_params = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"
        self.values.extend(where_params)

        if self.group_by_fields:
            sql += f" GROUP BY {', '.join(self.group_by_fields)}"

        having_clauses, having_params = self._build_having_clause()
        if having_clauses:
            sql += f" HAVING {having_clauses}"
        self.values.extend(having_params)

        if self.order_by_clauses:
            order_clauses = [f"`{field}` {order}" for field, order in self.order_by_clauses]
            sql += f" ORDER BY {', '.join(order_clauses)}"

        if self.limit is not None:
            sql += f" LIMIT {self.limit}"

        if self.offset is not None:
            sql += f" OFFSET {self.offset}"

        return sql, self.values


class OracleQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> Tuple[str, list]:
        self.optimize_query()
        sql = f"SELECT {', '.join(self.fields)} FROM {self.table_name}"

        for join in self.joins:
            sql += f" {join}"

        where_clause, where_params = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"
        self.values.extend(where_params)

        if self.group_by_fields:
            sql += f" GROUP BY {', '.join(self.group_by_fields)}"

        having_clauses, having_params = self._build_having_clause()
        if having_clauses:
            sql += f" HAVING {having_clauses}"
        self.values.extend(having_params)

        if self.order_by_clauses:
            order_clauses = [f"`{field}` {order}" for field, order in self.order_by_clauses]
            sql += f" ORDER BY {', '.join(order_clauses)}"

        if self.limit is not None:
            sql += f" FETCH FIRST {self.limit} ROWS ONLY"

        if self.offset is not None:
            sql += f" OFFSET {self.offset} ROWS"

        return sql, self.values


class SQLServerQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> Tuple[str, list]:
        self.optimize_query()
        sql = f"SELECT {', '.join(self.fields)} FROM {self.table_name}"

        for join in self.joins:
            sql += f" {join}"

        where_clause, where_params = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"
        self.values.extend(where_params)

        if self.group_by_fields:
            sql += f" GROUP BY {', '.join(self.group_by_fields)}"

        having_clauses, having_params = self._build_having_clause()
        if having_clauses:
            sql += f" HAVING {having_clauses}"
        self.values.extend(having_params)

        if self.order_by_clauses:
            order_clauses = [f"`{field}` {order}" for field, order in self.order_by_clauses]
            sql += f" ORDER BY {', '.join(order_clauses)}"

        if self.limit is not None:
            sql += f" OFFSET {self.offset} ROWS FETCH NEXT {self.limit} ROWS ONLY"

        return sql, self.values


class PostgreSQLQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> Tuple[str, list]:
        self.optimize_query()
        sql = f"SELECT {', '.join(self.fields)} FROM {self.table_name}"

        for join in self.joins:
            sql += f" {join}"

        where_clause, where_params = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"
        self.values.extend(where_params)

        if self.group_by_fields:
            sql += f" GROUP BY {', '.join(self.group_by_fields)}"

        having_clauses, having_params = self._build_having_clause()
        if having_clauses:
            sql += f" HAVING {having_clauses}"
        self.values.extend(having_params)

        if self.order_by_clauses:
            order_clauses = [f"`{field}` {order}" for field, order in self.order_by_clauses]
            sql += f" ORDER BY {', '.join(order_clauses)}"

        if self.limit is not None:
            sql += f" LIMIT {self.limit}"

        if self.offset is not None:
            sql += f" OFFSET {self.offset}"

        return sql, self.values


class MariaDBQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> Tuple[str, list]:
        self.optimize_query()
        sql = f"SELECT {', '.join(self.fields)} FROM `{self.table_name}`"

        for join in self.joins:
            sql += f" {join}"

        where_clause, where_params = self._build_where_clause()
        if where_clause:
            sql += f" WHERE {where_clause}"
        self.values.extend(where_params)

        if self.group_by_fields:
            sql += f" GROUP BY {', '.join(self.group_by_fields)}"

        having_clauses, having_params = self._build_having_clause()
        if having_clauses:
            sql += f" HAVING {having_clauses}"
        self.values.extend(having_params)

        if self.order_by_clauses:
            order_clauses = [f"`{field}` {order}" for field, order in self.order_by_clauses]
            sql += f" ORDER BY {', '.join(order_clauses)}"

        if self.limit is not None:
            sql += f" LIMIT {self.limit}"

        if self.offset is not None:
            sql += f" OFFSET {self.offset}"

        return sql, self.values


class MongoDBQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> Dict[str, Any]:
        query = {}
        projection = {field: 1 for field in self.fields} if "*" not in self.fields else {}

        if self.where_conditions:
            query = dict(self.where_conditions)

        options = {}
        if self.order_by_clauses:
            options["sort"] = [(field, -1 if desc else 1) for field, desc in self.order_by_clauses]

        if self.limit is not None:
            options["limit"] = self.limit

        if self.offset is not None:
            options["skip"] = self.offset

        return {"filter": query, "projection": projection, "options": options}


class RedisQueryBuilder(AbstractQueryBuilder):

    def build_query_sql(self) -> str:
        # Redis does not use SQL for query operations
        return "Redis does not use SQL for query operations."


class QueryBuilderFactory:

    def __init__(self, model):
        self.model = model
        self.builder = self._select_builder()

    def _select_builder(self):

        db_type = self.model.Meta.database_type

        if db_type == DataBaseType.mysql:
            return MySQLQueryBuilder(self.model)
        elif db_type == DataBaseType.sqlite:
            return SQLiteQueryBuilder(self.model)
        elif db_type == DataBaseType.oracle:
            return OracleQueryBuilder(self.model)
        elif db_type == DataBaseType.sqlserver:
            return SQLServerQueryBuilder(self.model)
        elif db_type == DataBaseType.postgresql:
            return PostgreSQLQueryBuilder(self.model)
        elif db_type == DataBaseType.mariadb:
            return MariaDBQueryBuilder(self.model)
        elif db_type == DataBaseType.mongodb:
            return MongoDBQueryBuilder(self.model)
        elif db_type == DataBaseType.redis:
            return RedisQueryBuilder(self.model)
        elif db_type == DataBaseType.csv:
            pass
        elif db_type == DataBaseType.file:
            pass
        else:
            raise ValueError(f"不支持的数据库类型: {self.model.Meta.database_type}")

    def build(self):
        return self.builder.build_query_sql()

    def __getattr__(self, item):
        if hasattr(self.builder, item):
            return getattr(self.builder, item)
        raise AttributeError(f"'{self.__class__.__name__}' 没有 '{item}' 方法或属性")
