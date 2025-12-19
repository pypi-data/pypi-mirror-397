import re
from datetime import datetime, date
from typing import Union

from AioSpider.exceptions import SqlException, StatusTags
from AioSpider.db.sql.base import SelectBase, InsertBase, CreateTableBase, AlterTableBase, escape_strings


class SQLiteSelect(SelectBase):

    SqliteFunc = (
        'ABS', 'LENGTH', 'LOWER', 'RANDOM', 'ROUND', 'UPPER', 'COUNT', 'MAX', 'MIN', 'SUM', 'AVG', 'TOTAL',
        'COALESCE', 'NULLIF', 'CAST', 'DATE', 'TIME', 'DATETIME', 'JULIANDAY', 'STRFTIME', 'LIKE', 'GLOB',
        'REGEXP', 'MATCH', 'SOUNDEX', 'LAST_INSERT_ROWID', 'CHANGES', 'TOTAL_CHANGES', 'REPLACE', 'LTRIM',
        'RTRIM', 'TRIM', 'SUBSTR', 'SUBSTRING', 'INSTR'
    )

    def build_field(self):
        if self._field is None:
            return '*'
        elif isinstance(self._field, str):
            return self._field
        elif isinstance(self._field, (list, tuple)):
            field = []
            for i in self._field:
                x = re.findall(r'^(.*)\(.*\)$', i) or re.findall(r'^(.*)\(.*\) ', i) or \
                    re.findall(r'^(.*)\(.*\)as', i)
                if x and x[0].upper() in self.SqliteFunc:
                    field.append(i)
                else:
                    field.append(f'"{i}"')
            return ",".join(field)
        else:
            raise SqlException(status=StatusTags.SqlFieldError)

    def build_order(self):
        if not self._order:
            return None

        if not isinstance(self._order, (list, tuple)):
            raise SqlException(status=StatusTags.SqlOrderError)

        order_list = [f'"{k}" {v}' for k, v in self._order]
        return ' ORDER BY ' + ",".join(order_list)

    def __str__(self):
        sql = f'SELECT {self.build_distinct()} {self.build_field()} FROM "{self._table}"'

        join = self.build_join()
        if join:
            sql += join

        where = self.build_where()
        if where:
            sql += where

        group = self.build_group()
        if group:
            sql += group

        having = self.build_having()
        if having:
            sql += having

        order = self.build_order()
        if order:
            sql += order

        limit = self.build_limit()
        if limit:
            sql += limit

        if self._subquery:
            sql = f'SELECT {self.build_field()} FROM ({sql}) AS "{self._subquery}"'

        union = self.build_union()
        if union:
            sql += union

        union_all = self.build_union_all()
        if union_all:
            sql += union_all

        return sql


class SqliteCreateTable(CreateTableBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_common_sql(self, field, cname, sql, default_format=None):

        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'

        if field.default is not None:
            if default_format:
                sql += f' DEFAULT {default_format(field.default)}'
            else:
                sql += f' DEFAULT "{field.default}"'

        return sql

    def build_auto_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        if field.primary:
            sql += f' NOT NULL PRIMARY KEY AUTOINCREMENT'
        else:
            sql += f' NOT NULL AUTOINCREMENT'
        return sql

    def build_stamp_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(field, cname, sql)
        return sql

    def build_time_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def build_date_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def build_datetime_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def __str__(self):

        cols_sql_list = self.build_cols_sql_list()

        sql = f'CREATE TABLE {self.table_name} (\n'
        sql += ',\n'.join(cols_sql_list)
        sql += f'\n);'

        index = ";\n".join([i for i in self.build_index_sql_list() if i])

        return f'{sql}\n{index}'


class SqliteAlterTable(AlterTableBase):

    def __init__(self, *args, **kwargs):
        super(SqliteAlterTable, self).__init__(*args, **kwargs)
        self.api = SqliteAlterAPI(self.table_name)

    def build_add_cols_sql(self, desc):

        condition = lambda cname, *args, **kwargs: cname.upper() not in [i.field.upper() for i in desc]
        return self.build_sql_list(self.api.build_add_column_sql, condition)

    def build_modify_cols_primary_sql(self, desc) -> str:
        condition = lambda cname, field: field.primary and not any(
            cname.upper() == i.field.upper() and i.key == 'PRI' for i in desc
        )
        return self.build_sql_list(self.api.build_modify_primary_sql, condition)

    def build_modify_cols_unique_sql(self, desc) -> str:
        condition = lambda cname, field: (
                not field.primary and field.unique and
                all(cname.upper() != des.field.upper() or des.key != 'UNI' for des in desc)
        )
        return self.build_sql_list(self.api.build_modify_unique_sql, condition)

    def build_modify_cols_index_sql(self, desc) -> str:
        condition = lambda cname, field: cname.upper() in [
            i.field.upper() for i in desc
            if not field.primary and not field.unique and field.db_index and i.key != 'MUL'
        ]
        return self.build_sql_list(self.api.build_modify_index_sql, condition)

    def build_modify_cols_uniun_index_sql(self, indexes):

        index_fields = [i for i in self.model.Meta.union_index if i in self.model.fields]
        new_index_fields = [f'`{i}`' for i in index_fields]
        index_name = f'union_idx_{self.model.table_name}_{"_".join(index_fields)}'

        # 创建索引
        if index_name not in [i['name'] for i in indexes]:
            return f'CREATE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'

        sql = []
        for i in indexes:
            if len(i['field']) == 1 or i['name'] != index_name:
                continue
            if set(i['field']) == set(index_fields) and not i['unique']:
                continue
            sql.append(f'DROP INDEX {index_name};')
            sql.append(f'CREATE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});')

        return sql

    def build_modify_cols_unique_uniun_index_sql(self, indexes):

        index_fields = [i for i in self.model.Meta.union_unique_index if i in self.model.fields]
        new_index_fields = [f'`{i}`' for i in index_fields]
        index_name = f'unique_idx_{self.model.table_name}_{"_".join(index_fields)}'

        # 创建索引
        if index_name not in [i['name'] for i in indexes]:
            return f'CREATE UNIQUE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'

        sql = []
        for i in indexes:
            if len(i['field']) == 1 or i['name'] != index_name:
                continue
            if set(i['field']) == set(index_fields) and i['unique']:
                continue
            sql.append(f'DROP INDEX {index_name};')
            sql.append(
                f'CREATE UNIQUE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'
            )

        return sql

    def build_modify_cols_type_sql(self, desc):

        def condition(cname, field):
            for des in desc:
                if cname.upper() != des.field.upper():
                    continue
                if hasattr(field, 'unsigned'):
                    if field.unsigned and (field.mapping[self.type] + ' UNSIGNED') != des.type:
                        return True
                    if not field.unsigned and field.mapping[self.type] != des.type:
                        return True
                else:
                    if field.mapping[self.type] != des.type:
                        return True
                return False

            return False

        return self.build_sql_list(self.api.build_modify_column_type_sql, condition)

    def build_change_column_type_sql(self, cname: str, new_type: str, max_length: int = None) -> str:
        """更改列类型 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column types directly. Consider using other workarounds."
        )

    def build_change_column_default_sql(self, cname: str, default_value: Union[str, int, float]) -> str:
        """更改列的默认值 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column default values directly. Consider using other workarounds."
        )

    def build_change_column_null_sql(self, cname: str, nullable: bool) -> str:
        """更改列的可空属性 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column nullability directly. Consider using other workarounds."
        )

    def build_drop_column_sql(self, cname: str) -> str:
        """删除列 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support dropping columns directly. Consider using other workarounds."
        )

    def build_rename_column_sql(self, old_cname: str, new_cname: str) -> str:
        """重命名列 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise 'ALTER TABLE old_table_name RENAME TO new_table_name;'

    def build_add_index_sql(self, cname: str, index_name: str, unique: bool = False) -> str:
        """添加索引"""
        sql = f'CREATE {"UNIQUE" if unique else ""} INDEX `{index_name}` ON `{self.table_name}`(`{cname}`);'
        return sql

    def build_drop_index_sql(self, index_name: str) -> str:
        """删除索引"""
        return f'DROP INDEX `{index_name}`;'

    def build_add_foreign_key_sql(self, cname: str, ref_table: str, ref_cname: str, constraint_name: str,
                                   on_delete: str = 'CASCADE', on_update: str = 'CASCADE') -> str:
        """添加外键约束 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support adding foreign keys directly. Consider using other workarounds."
        )

    def build_drop_foreign_key_sql(self, constraint_name: str) -> str:
        """删除外键约束 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support dropping foreign keys directly. Consider using other workarounds."
        )

    def build_change_table_collation_sql(self, collation: str) -> str:
        """更改表的排序规则 - SQLite 不支持更改表的排序规则"""
        raise NotImplementedError("SQLite does not support changing table collation.")

    def build_change_column_collation_sql(self, cname: str, collation: str) -> str:
        """更改列的排序规则 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column collation directly. Consider using other workarounds."
        )

    def build_rename_table_sql(self, new_name: str) -> str:
        """重命名表"""
        return self.api.build_rename_table_sql(new_name)


class SqliteAlterAPI:

    def __init__(self, table_name):
        self.table_name = table_name

    def build_rename_table_sql(self, new_name: str) -> str:
        """重命名表"""
        return f'ALTER TABLE `{self.table_name}` RENAME TO `{new_name}`'

    def build_add_column_sql(self, cname: str, field, *args, **kwargs) -> str:
        """添加列"""

        sql = f'ALTER TABLE "{self.table_name}" ADD COLUMN "{cname}" {field.mapping["stype"]}'

        if field.max_length is not None:
            sql += f'({field.max_length})'

        if hasattr(field, 'unsigned') and field.unsigned:
            sql += ' UNSIGNED'

        if field.default is not None:
            if isinstance(field.default, (str, date, datetime)):
                if field.default == 'CURRENT_TIMESTAMP':
                    sql += f' DEFAULT {field.default}'
                else:
                    sql += f' DEFAULT {escape_strings(field.default)}'
            else:
                sql += f' DEFAULT {field.default}'

        if not field.null:
            sql += f' NOT NULL'

        return sql

    def build_modify_column_type_sql(self, cname: str, field, *args, **kwargs) -> str:
        """修改字段类型"""
        return 'True'

    def build_modify_primary_sql(self, cname: str, field, *args, **kwargs) -> str:
        return 'True'

    def build_modify_unique_sql(self, cname: str, *args, **kwargs) -> str:
        return 'True'

    def build_modify_index_sql(self, cname: str, *args, **kwargs) -> str:
        return 'True'


class SqliteInsert(InsertBase):

    def build_insert_sql(self):
        """插入数据"""

        field = ','.join([f'`{i}`' for i in self._field])
        value = ',\n'.join([
            (
                '(' + ','.join([f"'{escape_strings(i)}'" for i in item]) + ')'
            ) for item in self._values
        ])
        value = value.replace('\'\"', "'").replace('\"\'', "'")

        return f"INSERT INTO `{self._table}` ({field}) VALUES {value}"

    def build_insert_update_sql(self):

        field = ','.join([f'`{i}`' for i in self._field])
        sql = f'{self.build_insert_sql()} on conflict do update set ({field}) = (' \
              f'{",".join([f"EXCLUDED.`{i}`" for i in self._field])})'

        return sql


class SQLiteUpdate:

    def __init__(self, table: str, item: dict, where: dict = None):
        self._table = table
        self._item = item
        self._where = where

    def build_update_sql(self):
        if not self._item:
            return ''

        return f'''UPDATE `{self._table}` SET {', '.join([f"`{k}` = '{v}'" for k, v in self._item.items()])} 
        WHERE {' AND '.join([f"`{k}` = '{v}'" for k, v in self._where.items()])};'''

    def __str__(self):
        return self.build_update_sql()

    __repr__ = __str__
