from typing import Union, Optional, List, Literal, TypeVar, Iterator

import pandas as pd
from AioSpider.constants import DataBaseType
from AioSpider.db.sql import MysqlCreateTable, SqliteCreateTable

DataType = Literal['list', 'dict', 'pd', 'iter', 'model']
RType = TypeVar('RType', list, dict, pd.DataFrame, Iterator)


class QuerySet:

    def __init__(self, model=None):
        self.model = model
        self._field = None
        self._where = None
        self._count = None
        self._offset = None
        self._order = None
        self._desc = False
        self._group = None
        self._rtype: DataType = 'list'

    def __get__(self, instance, owner):
        return self.__class__(model=owner)

    @property
    def database(self):
        return self.model.database

    @property
    def table(self):
        return self.model.Meta.tb_name

    def table_exist(self):
        return self.database.table_exist(table=self.table)

    def create_table(self, *args, **kwargs):

        from AioSpider.models import SQLiteModel, MySQLModel

        if issubclass(self.model, SQLiteModel):
            str(SqliteCreateTable(self.model))

        if issubclass(self.model, MySQLModel):
            sql = str(MysqlCreateTable(self.model))

        return self.database.create_table(sql=sql)

    def filter(self, **kwargs):

        if not kwargs:
            return self

        operators = {'gt': '>', 'gte': '>=', 'lt': '<', 'lte': '<=', 'isnull': 'is null'}

        where = {}

        for k, v in kwargs.items():
            if '__' in k:
                field, operator = k.split('__')
                if operator == 'isnull':
                    condition = {'is null': ''} if v else {'is not null': ''}
                elif operator == 'in':
                    condition = {'in': v}
                elif operator == 'notin':
                    condition = {'not in': v}
                elif operator == 'contains':
                    condition = {'like': f'%%{v}%%'}
                else:
                    condition = {operators.get(operator, '='): v}
                where.setdefault(field, {}).update(condition)
            else:
                where[k] = v

        if self._where is None:
            self._where = where
        else:
            self._where.update(where)

        return self

    def only(self, *args):

        if not args:
            return self

        if self._field is None:
            self._field = args
        else:
            for i in args:
                if i in self._field:
                    continue
                self._field = self._field + (i,)

        return self

    def exclude(self, *args):

        if not args:
            return self

        if self._field is None:
            self._field = tuple([i for i in self.model.fields if i not in args])
        else:
            for i in self.model.fields:
                if i in self._field or i not in args:
                    continue
                self._field = self._field + (i,)

        return self

    def type(self, rtype: RType = 'list'):
        self._rtype = rtype
        return self

    def limit(self, n: int):
        self._count = n
        return self

    def offset(self, n: int):
        self._offset = n
        return self

    def exists(self):
        return any(self.get())

    def order_by(self, *args, desc: bool = False):

        if not args:
            return self

        if self._order is None:
            self._order = list(set(args))
        else:
            self._order = list(set(self._order.extend(args)))

        self._desc = desc

        return self

    def group_by(self, *args):

        if not args:
            return self

        if self._group is None:
            self._group = list(set(args))
        else:
            self._group = list(set(self._group.extend(args)))

        return self

    def count(self, field=None):
        if field is None:
            self._field = ('count(*)',) if self._field is None else self._field + ('count(*)',)
        else:
            self._field = (f'count(`{field}`)',) if self._field is None else self._field + (f'count(`{field}`)',)
        return self.get(flat=True)

    def get(self, flat=False, callback=None, **kwargs):

        data = self.filter(**kwargs).limit(1).all(flat=flat)
        data = data[0] if data else data

        return data if callback is None else callback(data)

    def all(self, flat=False, callback=None, **kwargs):

        self = self.filter(**kwargs)

        if self.model.Meta.engine == DataBaseType.redis:
            data = self.database.find(
                table=self.table, data_type=self.model.Meta.data_type, field=self._field, offset=self._offset,
                desc=self._desc, limit=self._count, order=self._order, where=self._where
            )
        else:
            data = self.database.find(
                table=self.table, field=self._field, where=self._where, limit=self._count, offset=self._offset,
                order=self._order, desc=self._desc, group=self._group
            )

        if self._rtype == 'list':
            data = data if data else []
        elif self._rtype == 'dict':
            data = data[0] if data else dict()
        elif self._rtype == 'pd':
            data = pd.DataFrame(data)
        elif self._rtype == 'model':
            data = [self.model(i) for i in data]
        else:
            data = iter(data)

        if callback is None:
            return [
                tuple(i[k] for k in i) if len(i.values()) > 1 else next(iter(i.values()))
                for i in data
            ] if flat else data
        else:
            return callback(
                [
                    tuple(i[k] for k in i) if len(i.values()) > 1 else next(
                        iter(i.values())) for i in data
                ] if flat else data
            )

    def create(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.model.fields}
        if self.model.Meta.engine == DataBaseType.redis:
            return self.database.insert(
                table=self.table, data_type=self.model.Meta.data_type, items=self.model(kwargs).make_item(),
                auto_update=self.model.Meta.auto_update
            )
        else:
            item = self.model(kwargs).make_item()
            return self.database.insert(table=self.table, items=item, auto_update=self.model.Meta.auto_update)

    def creates(self, items: Union[list, dict]):
        if isinstance(items, dict):
            items = [items]
        items = [{k: v for k, v in i.items() if k in self.model.fields} for i in items]
        if self.model.Meta.engine == DataBaseType.redis:
            return self.database.insert(
                table=self.table, data_type=self.model.Meta.data_type,
                items=[self.model(i).make_item() for i in items],
                auto_update=self.model.Meta.auto_update
            )
        else:
            items = [self.model(i).make_item() for i in items]
            return self.database.insert(table=self.table, items=items, auto_update=self.model.Meta.auto_update)

    def update(self, **kwargs):
        if self.model.Meta.engine == DataBaseType.redis:
            return self.database.update(
                table=self.table, data_type=self.model.Meta.data_type, item=kwargs, where=self._where
            )
        else:
            return self.database.update(table=self.table, item=kwargs, where=self._where)

    def delete(self):
        return self.database.delete(table=self.table, where=self._where)

    def execute(self, sql):
        return self.database.execute(sql)

    def fetch(self, sql):
        return self.database._get(sql)
