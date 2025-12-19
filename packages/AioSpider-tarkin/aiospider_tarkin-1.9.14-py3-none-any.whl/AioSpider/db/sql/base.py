from abc import abstractmethod
from pathlib import Path
from datetime import datetime, date, time
from typing import Union, Optional

from pymysql.converters import escape_string

from AioSpider.objects import DataBaseType
from AioSpider.exceptions import SqlException


def escape_strings(value):
    """转移数据类型"""

    if isinstance(value, str):
        escaped_value = escape_string(value)
        return f'"{escaped_value}"'
    elif isinstance(value, Path):
        return '"' + escape_string(str(value)).replace('"', '""') + '"'
    elif isinstance(value, (datetime, date, time)):
        return '"' + str(value) + '"'
    elif isinstance(value, bool):
        return str(int(value))
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return 'NULL'
    elif isinstance(value, (list, tuple)):
        return ','.join(escape_strings(item) for item in value)
    else:
        return escape_string(str(value))


operator = ('>=', '<=', '=', '>', '<')
logical = ('is null', 'is not null', 'in', 'not in', 'like')


def operator_compare(k, x, y):
    return f'`{k}` {x} {escape_strings(y) if y else y}'



def logical_compare(k, x, y):
    if x in ('in', 'not in'):
        return (f'`{k}` {"=" if x == "in" else "!="} {y[0]}' if len(y) == 1 else f'`{k}` {x} {tuple(y)}')  if y else ''
    else:
        return f'`{k}` {x} {escape_strings(y) if y else y}'
    

class SelectBase:
    """
        生成查询语句
        @params:
            table: 表名
            field: 查询字段约束
            where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
            group: 分组
            having: 筛选分组后的各组数据
            order: 排序
            desc: 是否倒序
            limit: 数量
            offset: 偏移量
            join: 多表连接查询,
            subquery: 子查询,
            union: 联合查询,
            union_all: 联合查询,
            distinct: 去重行,
    """

    def __init__(
            self,
            table: str,
            field: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None,
            group: Union[list, tuple] = None,
            having: Optional[dict] = None,
            order: Union[list, tuple] = None,
            desc: bool = False,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            join: Optional[list] = None,
            subquery: Optional[str] = None,
            union: Optional[str] = None,
            union_all: Optional[str] = None,
            distinct: bool = False
    ):
        self._table = table
        self._field = field
        self._where = where
        self._group = group
        self._having = having
        self._order = order
        self._limit = limit
        self._offset = offset
        self._desc = desc
        self._join = join
        self._subquery = subquery
        self._union = union
        self._union_all = union_all
        self._distinct = distinct

    def __str__(self):
        pass

    __repr__ = __str__

    def build_field(self):
        pass

    def build_where(self):

        if not self._where:
            return None

        assert isinstance(self._where, dict), SqlException(status=StatusTags.SqlWhereError)

        where_list = []

        for k, v in self._where.items():
            if isinstance(v, dict):
                for x, y in v.items():
                    if x in operator:
                        where_list.append(operator_compare(k, x, y))
                    elif x in logical:
                        where_list.append(logical_compare(k, x, y))
            else:
                where_list.append(f'`{k}`={escape_strings(v)}')

        if ' AND '.join([i for i in where_list if i]):
            return ' WHERE ' + ' AND '.join([i for i in where_list if i])
        else:
            return None

    def build_group(self):
        if self._group is None:
            return None
        elif isinstance(self._group, str):
            if '`' not in self._group:
                self._group = f'`{self._group}`'
            return f' GROUP BY {self._group}'
        elif isinstance(self._group, (list, tuple)):
            self._group = [f'`{i}`' for i in self._group if '`' not in i]
            return f' GROUP BY {",".join(self._group)}'
        else:
            raise SqlException(status=StatusTags.SqlOrderError)

    def build_having(self):

        if self._having is None:
            return None

        assert isinstance(self._having, dict), SqlException(status=StatusTags.SqlHavingError)

        having_list = [
            operator_compare(k, v) if isinstance(v, dict) else [f'`{k}`={escape_strings(v)}']
            for k, v in self._having.items()
        ]
        having_list = [j for i in having_list for j in i if j]

        return ' HAVING ' + ' AND '.join(having_list)

    def build_order(self):
        pass

    def build_limit(self):

        if self._limit is None:
            return None

        return f' LIMIT {self._limit}'

    def build_offset(self):

        if self._offset is None:
            return None

        return f' OFFSET {self._offset}'

    def build_desc(self):
        return ' DESC' if self._desc else None

    def build_distinct(self):
        return 'DISTINCT' if self._distinct else ''

    def build_join(self):

        if not self._join:
            return None

        join_str = ''
        for join_clause in self._join:
            join_type = join_clause.get('type', 'INNER').upper()
            join_table = join_clause['table']
            join_on = join_clause['on']
            join_str += f' {join_type} JOIN `{join_table}` ON {join_on}'

        return join_str

    def build_union(self):
        return f' UNION {self._union}' if self._union else None

    def build_union_all(self):
        return f' UNION ALL {self._union_all}' if self._union_all else None


class InsertBase:

    def __init__(self, table: str, field: Union[list, tuple], values: Union[list, tuple], auto_update: bool = False):
        self._table = table
        self._field = field
        self._values = values
        self._auto_update = auto_update

    def build_insert_sql(self):
        """插入数据"""

        field = ','.join([f'`{i}`' for i in self._field])
        value = ',\n'.join([
            (
                '(' + ','.join([escape_strings(i) for i in item]) + ')'
            ) for item in self._values
        ])

        return f'INSERT INTO `{self._table}` ({field}) VALUES {value}'

    @abstractmethod
    def build_insert_update_sql(self): ...

    def __str__(self):

        if self._auto_update:
            return self.build_insert_update_sql()
        else:
            return self.build_insert_sql()

    __repr__ = __str__


class CreateTableBase:

    def __init__(self, model):
        self.model = model
        self.type = 'mtype' if model.Meta.engine == 'mysql' else 'stype'
        self.table_name = self.model.table_name

    def __str__(self):
        pass

    __repr__ = __str__
    
    @abstractmethod
    def build_common_sql(self, field, cname, sql, default_format=None):
        pass

    @abstractmethod
    def build_auto_sql(self, field, cname): ...

    @abstractmethod
    def build_stamp_sql(self, field, cname): ...

    @abstractmethod
    def build_time_sql(self, field, cname): ...

    @abstractmethod
    def build_date_sql(self, field, cname): ...

    @abstractmethod
    def build_datetime_sql(self, field, cname): ...
    
    def build_json_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(field, cname, sql)
        return sql

    def build_column_sql(self, field, cname):

        build_method_mapping = {
            'AutoIntField': self.build_auto_sql,
            'VARCHAR': self.build_varchar_sql,
            'TINYINT': self.build_int_sql,
            'SMALLINT': self.build_int_sql,
            'INT': self.build_int_sql,
            'BIGINT': self.build_int_sql,
            'MEDIUMINT': self.build_int_sql,
            'TINYINTEGER': self.build_int_sql,
            'SMALLINTEGER': self.build_int_sql,
            'INTEGER': self.build_int_sql,
            'MEDIUMINTEGER': self.build_int_sql,
            'BIGINTEGER': self.build_int_sql,
            'FLOAT': self.build_float_sql,
            'DOUBLE': self.build_float_sql,
            'BOOLEAN': self.build_boolean_sql,
            'TIMESTAMP': self.build_stamp_sql,
            'TIME': self.build_time_sql,
            'DATE': self.build_date_sql,
            'DATETIME': self.build_datetime_sql,
            'TEXT': self.build_text_sql,
            'MEDIUMTEXT': self.build_text_sql,
            'LONGTEXT': self.build_text_sql,
            'DECIMAL': self.build_decimal_sql,
            'ENUM': self.build_enum_sql,
            'FOREIGN KEY': self.build_foreign_key_sql,
            'JSON': self.build_json_sql,
        }

        key = field.__class__.__name__ if field.__class__.__name__ == 'AutoIntField' else field.mapping[self.type]
        build_method = build_method_mapping.get(key)

        if build_method:
            return build_method(field, cname)

        return None

    def build_varchar_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}({field.max_length})'
        return self.build_common_sql(field, cname, sql)

    def build_int_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        if hasattr(field, 'unsigned') and field.unsigned:
            sql += f' UNSIGNED'
        return self.build_common_sql(field, cname, sql)

    def build_float_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        return self.build_common_sql(field, cname, sql)

    def build_boolean_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        return self.build_common_sql(field, cname, sql)

    def build_text_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        return self.build_common_sql(field, cname, sql)

    def build_decimal_sql(self, field, cname):

        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}({field.max_length},{field.precision})'

        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'
        elif field.unique:
            sql += f' UNIQUE'

        if field.default is not None:
            sql += f' DEFAULT {field.default}'

        sql += f' COMMENT "{field.name}"'

        return sql

    def build_enum_sql(self, field, cname):

        enum_values = ','.join([f'"{value}"' for value in field.choices])
        sql = f'`{field.db_column or cname or field.name}` ENUM({enum_values})'

        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'
        elif field.unique:
            sql += f' UNIQUE'

        if field.default:
            sql += f' DEFAULT "{field.default}"'

        sql += f' COMMENT "{field.name}"'

        return sql

    def build_foreign_key_sql(self, field, cname):

        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql += f' REFERENCES {field.reference_table}({field.reference_column})'

        if field.on_delete:
            sql += f' ON DELETE {field.on_delete}'
        if field.on_update:
            sql += f' ON UPDATE {field.on_update}'

        return sql

    def build_index_sql(self, field, cname):

        if not field.db_index:
            return None

        if field.db_index is True:
            if field.primary:
                return None
            elif field.unique:
                index = UniqueIndexField
            else:
                index = NormalIndexField
        else:
            index = field.db_index

        if self.model.Meta.engine == DataBaseType.mysql:
            return index(self.table_name, cname).index_mysql()
        elif self.model.Meta.engine == DataBaseType.sqlite:
            return index(self.table_name, cname).index_sqlite()
        else:
            return None

    def build_cols_sql_list(self):
        return [
            self.build_column_sql(field=field, cname=f)
            for f, field in self.model.fields.items() if field
        ]

    def build_index_sql_list(self):

        index_sql = []

        for f, field in self.model.fields.items():
            if not field or field.primary:
                continue
            if self.model.Meta.engine == 'mysql' and field.unique:
                continue
            index_sql.append(self.build_index_sql(field=field, cname=f))
            
        # 联合索引
        if self.model.Meta.union_index is not None:
            index_fields = [i for i in self.model.Meta.union_index if i in self.model.fields]
            if index_fields:
                index = UnionIndexField(self.table_name, index_fields)
                if self.model.Meta.engine == DataBaseType.mysql:
                    index_sql.append(index.index_mysql())
                elif self.model.Meta.engine == DataBaseType.sqlite:
                    index_sql.append(index.index_sqlite())
                
        # 联合唯一索引
        if self.model.Meta.union_unique_index is not None:
            index_fields = [i for i in self.model.Meta.union_unique_index if i in self.model.fields]
            if index_fields:
                index = UniqueUnionIndexField(self.table_name, index_fields)
                if self.model.Meta.engine == DataBaseType.mysql:
                    index_sql.append(index.index_mysql())
                elif self.model.Meta.engine == DataBaseType.sqlite:
                    index_sql.append(index.index_sqlite())

        return (i for i in index_sql if i)


class AlterTableBase:

    def __init__(self, model):
        self.model = model
        self.type = 'mtype' if model.Meta.engine == 'mysql' else 'stype'
        self.table_name = self.model.table_name

    def __str__(self):
        pass

    __repr__ = __str__

    def build_sql_list(self, method_name: str, condition: callable) -> str:
        cols_sql = []

        for f, field in self.model.fields.items():
            if not field or not condition(f, field):
                continue
            cols_sql.append(method_name(f, field))

        return ';\n'.join(cols_sql)
