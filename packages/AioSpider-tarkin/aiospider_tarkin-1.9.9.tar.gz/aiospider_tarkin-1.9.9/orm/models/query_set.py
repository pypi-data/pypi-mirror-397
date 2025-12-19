import math
from typing import Literal, TypeVar, Iterator

import pandas as pd
from AioSpider import logger
from AioSpider.objects import AdapterResultType, DataBaseType
from AioSpider.exceptions import ORMException

from ..migrations import MigrationManager
from ..builder.factory import BuilderFactory
from ..adapter.factory import DatabaseAdapterFactory, AsyncDatabaseAdapterFactory
from ..builder.aggregates import Aggregate, Count, Sum, Avg, Max, Min, Std, Variance, GroupConcat

__all__ = ['QuerySet', 'AsyncQuerySet']

DataType = Literal['list', 'dict', 'pd', 'iter', 'model']
RType = TypeVar('RType', list, dict, pd.DataFrame, Iterator)


class QuerySet:

    def __init__(self, model=None):
        self.model = model
        self.db_adapter = None
        self.builder_factory = BuilderFactory(self.model)
        self.query_builder = self.builder_factory.get_query_builder()
        self.insert_builder = self.builder_factory.get_insert_builder()
        self.update_builder = self.builder_factory.get_update_builder()
        self.delete_builder = self.builder_factory.get_delete_builder()

    def get_adapter(self):
        return DatabaseAdapterFactory.create_adapter(self.model.Meta.database_type, self.model.Meta.alias)

    @classmethod
    def from_model(cls, model):
        self = cls(model=model)
        self.db_adapter = self.get_adapter()
        return self

    def migrate(self):
        migration_manager = MigrationManager.from_model(self.model)
        migration_manager.apply_schema_changes()

    def filter(self, **kwargs):
        self.query_builder.where(**kwargs)
        return self

    def update_filter(self, **kwargs):
        self.update_builder.where(**kwargs)
        return self

    def delete_filter(self, **kwargs):
        self.delete_builder.where(**kwargs)
        return self

    def only(self, *fields):
        self.query_builder.select(*fields)
        return self

    def defer(self, *fields):
        self.query_builder.defer(*fields)
        return self
    
    def exclude(self, **kwargs):
        self.query_builder.exclude(**kwargs)
        return self

    def subquery(self, subquery: 'QuerySet', alias: str):
        self.query_builder.subquery(subquery.query_builder, alias)
        return self

    def join(self, table: str, condition: str, join_type: str = 'INNER'):
        self.query_builder.join(table, condition, join_type)
        return self

    def left_join(self, table: str, condition: str):
        return self.join(table, condition, 'LEFT')

    def right_join(self, table: str, condition: str):
        return self.join(table, condition, 'RIGHT')

    def outer_join(self, table: str, condition: str):
        return self.join(table, condition, 'FULL OUTER')

    def limit(self, n: int):
        current_offset = self.query_builder.offset or 0
        self.query_builder.limit_offset(n, current_offset)
        return self

    def offset(self, n: int):
        current_limit = self.query_builder.limit or 0
        self.query_builder.limit_offset(current_limit, n)
        return self

    def order_by(self, *fields):
        self.query_builder.order_by(*fields)
        return self

    def group_by(self, *args):
        self.query_builder.group_by(*args)
        return self

    def having(self, *conditions, **kwargs):
        self.query_builder.having(*conditions, **kwargs)
        return self

    def annotate(self, **kwargs):
        self.query_builder.annotate(**kwargs)
        return self

    def aggregate(self, *args, **kwargs):
        aggregates = list(args) + [v for v in kwargs.values() if isinstance(v, Aggregate)]
        self.query_builder.annotate(**{f"agg_{i}": agg for i, agg in enumerate(aggregates)})
        result = self.get()
        if result:
            return {k: v for k, v in result.items() if k.startswith('agg_')}
        return None

    def count(self, field: str = "*"):
        return  self.aggregate(Count(field))['agg_0']

    def sum(self, field):
        return self.aggregate(Sum(field))['agg_0']

    def avg(self, field):
        return self.aggregate(Avg(field))['agg_0']

    def max(self, field):
        return self.aggregate(Max(field))['agg_0']

    def min(self, field):
        return self.aggregate(Min(field))['agg_0']

    def std(self, field):
        if self.model.Meta.database_type == DataBaseType.sqlite:
            return math.sqrt(self.variance(field))
        return self.aggregate(Std(field))['agg_0']

    def variance(self, field):
        if self.model.Meta.database_type == DataBaseType.sqlite:
            avg = self.avg(field)
            values = self.only(field).all()
            if not values:
                return 0
            return round(sum((value - avg) ** 2 for value in values) / len(values), 3)
        return self.aggregate(Variance(field))['agg_0']

    def group_concat(self, field, separator=","):
        return self.aggregate(GroupConcat(field, separator))['agg_0']
    
    def exists(self):
        data = self.only('id').get()
        return bool(data)

    def create_table(self):
        sql = self.builder_factory.get_table_builder().build()
        return self.db_adapter.execute(sql, None, return_type=AdapterResultType.affected_rows)

    def get(self, flat=False, callback=None, type: DataType = 'dict'):
        def _format_data(data, type: DataType):
            if isinstance(data, list):
                data = data and data[0] or {}
            if type == 'dict':
                return data
            elif type == 'model':
                return self.model(**data)
            elif type == 'pd':
                return pd.Series(data)
            else:
                raise ORMException(f"无效的ORM返回类型: {type}")

        def _flatten_data(data):
            values = tuple(data.values())
            if not values:
                data = tuple(None for _ in self.query_builder.fields)
            return values[0] if len(values) == 1 else values

        try:
            self = self.limit(1)
            query, params = self.query_builder.build()
            data = self.db_adapter.fetch_all(query, tuple(params))
            data = _format_data(data, type)

            if callback is None:
                data = _flatten_data(data) if flat else data
            else:
                data = callback(_flatten_data(data) if flat else data)

            self.query_builder.reset()
            return data
        except Exception as e:
            logger.level5(msg=f"查询失败，错误信息：{e}")
            self.query_builder.reset()
    
    def all(self, flat=False, callback=None, type: DataType = 'list'):

        def _format_data(data, type: DataType):
            if type == 'list':
                return data
            elif type == 'pd':
                return pd.DataFrame(data)
            elif type == 'model':
                return [self.model(**i) for i in data]
            else:
                return iter(data)

        def _flatten_data(data):
            if not data:
                return [None] if len(self.query_builder.fields) == 1 else [
                    tuple(None for _ in self.query_builder.fields)
                ]
            return [tuple(i.values()) if len(i) > 1 else next(iter(i.values())) for i in data]

        try:
            query, params = self.query_builder.build()
            data = self.db_adapter.fetch_all(query, tuple(params))
            data = _format_data(data, type)

            if callback is None:
                data = _flatten_data(data) if flat else data
            else:
                data = callback(_flatten_data(data) if flat else data)

            self.query_builder.reset()
            return data
        except Exception as e:
            logger.level5(msg=f"查询失败，错误信息：{e}")
            self.query_builder.reset()

    def create(self, **kwargs):
        model = self.model(**kwargs)
        self.insert_builder.add_row(model.make_item())

        sql, values = self.insert_builder.build()
        model.id = self.db_adapter.execute(sql, values[0] if values else None, return_type=AdapterResultType.lastrowid)
        
        self.insert_builder.reset()

        return model

    def create_or_update(self, **kwargs):
        model = self.model(**kwargs)
        item = model.make_item()

        self.insert_builder.add_row(item).on_duplicate_key_update(item)
        sql, values = self.insert_builder.build()
        model.id = self.db_adapter.execute(sql, values[0] if values else None, return_type=AdapterResultType.lastrowid)

        self.insert_builder.reset()

        return model

    def bulk_create(self, models: list, batch_size=1000):
        for i in range(0, len(models), batch_size):
            batch = models[i:i+batch_size]
            for model in batch:
                self.insert_builder.add_row(model.make_item())
            sql, values = self.insert_builder.build()
            self.db_adapter.execute_many(sql, values, return_type=AdapterResultType.affected_rows)

            self.insert_builder.reset()

    def bulk_create_or_update(self, models: list, batch_size=1000):
        for i in range(0, len(models), batch_size):
            batch = models[i:i+batch_size]
            for model in batch:
                item = model.make_item()
                self.insert_builder.add_row(item).on_duplicate_key_update(item)

            sql, values = self.insert_builder.build()
            self.db_adapter.execute_many(sql, values, return_type=AdapterResultType.affected_rows)

            self.insert_builder.reset()

    def update(self, **kwargs):
        for field, value in kwargs.items():
            self.update_builder.set(field, value)

        sql, values = self.update_builder.build()
        self.db_adapter.execute(sql, values, return_type=AdapterResultType.affected_rows)

        self.update_builder.reset()

    def delete(self):
        sql, values = self.delete_builder.build()
        self.db_adapter.execute(sql, values, return_type=AdapterResultType.affected_rows)
        self.delete_builder.reset()

    def fetch(self, sql, params=None):
        return self.db_adapter.fetch_all(sql, params)

    def execute(self, sql, params=None):
        return self.db_adapter.execute(sql, params)


class AsyncQuerySet(QuerySet):

    async def get_adapter(self):
        return await AsyncDatabaseAdapterFactory.create_adapter(self.model.Meta.database_type, self.model.Meta.alias)

    @classmethod
    async def from_model(cls, model):
        self = cls(model=model)
        self.db_adapter = await self.get_adapter()
        return self

    async def aggregate(self, *args, **kwargs):
        aggregates = list(args) + [v for v in kwargs.values() if isinstance(v, Aggregate)]
        self.query_builder.annotate(**{f"agg_{i}": agg for i, agg in enumerate(aggregates)})
        result = await self.get()
        if result:
            return {k: v for k, v in result.items() if k.startswith('agg_')}
        return None

    async def count(self, field: str = "*"):
        return (await self.aggregate(Count(field)))['agg_0']

    async def sum(self, field):
        return await self.aggregate(Sum(field))['agg_0']

    async def avg(self, field):
        return await self.aggregate(Avg(field))['agg_0']

    async def max(self, field):
        return await self.aggregate(Max(field))['agg_0']

    async def min(self, field):
        return await self.aggregate(Min(field))['agg_0']

    async def std(self, field):
        if self.model.Meta.database_type == DataBaseType.sqlite:
            return math.sqrt(self.variance(field))
        return await self.aggregate(Std(field))['agg_0']

    async def variance(self, field):
        if self.model.Meta.database_type == DataBaseType.sqlite:
            avg = self.avg(field)
            values = await self.only(field).all()
            if not values:
                return 0
            return round(sum((value - avg) ** 2 for value in values) / len(values), 3)
        return await self.aggregate(Variance(field))['agg_0']

    async def group_concat(self, field, separator=","):
        return await self.aggregate(GroupConcat(field, separator))['agg_0']

    async def exists(self):
        data = await self.only('id').get()
        return bool(data)

    async def create_table(self):
        sql = self.builder_factory.get_table_builder().build()
        return await self.db_adapter.execute(sql, None)

    def query_page(self, page: int, count: int):
        return self.offset((page - 1) * count).limit(count)
        
    async def get(self, flat=False, callback=None, type: DataType = 'dict'):

        def _format_data(data, type: DataType):
            if isinstance(data, list):
                data = data and data[0] or {}
            if type == 'dict':
                return data
            elif type == 'model':
                return self.model(**data)
            elif type == 'pd':
                return pd.Series(data)
            else:
                raise ORMException(f"无效的ORM返回类型: {type}")

        def _flatten_data(data):
            values = tuple(data.values())
            if not values:
                data = tuple(None for _ in self.query_builder.fields)
            return values[0] if len(values) == 1 else values

        try:
            self = self.limit(1)
            query, params = self.query_builder.build()
            data = await self.db_adapter.fetch_all(query, params)
            data = _format_data(data, type)

            if callback is None:
                data = _flatten_data(data) if flat else data
            else:
                data = callback(_flatten_data(data) if flat else data)

            self.query_builder.reset()
            return data
        except Exception as e:
            logger.level5(msg=f"查询失败，错误信息：{e}")
            self.query_builder.reset()

    async def all(self, flat=False, callback=None, type: DataType = 'list'):

        def _format_data(data, type: DataType):
            if type == 'list':
                return data
            elif type == 'pd':
                return pd.DataFrame(data)
            elif type == 'model':
                return [self.model(**i) for i in data]
            else:
                return iter(data)

        def _flatten_data(data):
            if not data:
                return [None] if len(self.query_builder.fields) == 1 else [
                    tuple(None for _ in self.query_builder.fields)
                ]
            return [tuple(i.values()) if len(i) > 1 else next(iter(i.values())) for i in data]

        try:
            query, params = self.query_builder.build()
            data = await self.db_adapter.fetch_all(query, tuple(params))
            data = _format_data(data, type)

            if callback is None:
                data = _flatten_data(data) if flat else data
            else:
                data = callback(_flatten_data(data) if flat else data)
                
            self.query_builder.reset()
            return data
        except Exception as e:
            logger.level5(msg=f"查询失败，错误信息：{e}")
            self.query_builder.reset()

    async def create(self, **kwargs):
        model = self.model(**kwargs)
        self.insert_builder.add_row(model.make_item())
        sql, values = self.insert_builder.build()
        model.id = await self.db_adapter.execute(sql, values, return_type=AdapterResultType.lastrowid)

        self.insert_builder.reset()
        return model

    async def create_or_update(self, **kwargs):
        model = self.model(**kwargs)
        item = model.make_item()

        self.insert_builder.add_row(item).on_duplicate_key_update(item)
        sql, values = self.insert_builder.build()
        model.id = await self.db_adapter.execute(sql, values, return_type=AdapterResultType.lastrowid)

        self.insert_builder.reset()
        return model

    async def bulk_create(self, models: list, batch_size=1000):
        affected = 0
        for i in range(0, len(models), batch_size):
            batch = models[i:i+batch_size]
            for model in batch:
                self.insert_builder.add_row(model.make_item())

            sql, values = self.insert_builder.build()
            affected += await self.db_adapter.execute_many(sql, values, return_type=AdapterResultType.affected_rows)
            self.insert_builder.reset()

        return affected

    async def bulk_create_or_update(self, models: list, batch_size=1000):
        affected = 0
        insert_builder = self.builder_factory.get_insert_builder()
        for i in range(0, len(models), batch_size): 
            batch = models[i:i+batch_size]
            for model in batch:
                item = model.make_item()
                insert_builder.add_row(item).on_duplicate_key_update(item)

            sql, values = insert_builder.build()
            affected += await self.db_adapter.execute_many(sql, values, return_type=AdapterResultType.affected_rows)
            self.insert_builder.reset()

        return affected

    async def update(self, **kwargs):
        for field, value in kwargs.items():
            self.update_builder.set(field, value)

        sql, values = self.update_builder.build()
        await self.db_adapter.execute(sql, values, return_type=AdapterResultType.affected_rows)
        self.update_builder.reset()

    async def delete(self):
        sql, values = self.delete_builder.build()
        await self.db_adapter.execute(sql, values, return_type=AdapterResultType.affected_rows)
        self.delete_builder.reset()

    async def execute(self, sql, params=None):
        return await self.db_adapter.execute(sql, params)
