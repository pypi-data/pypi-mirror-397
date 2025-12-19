import re
from datetime import datetime, date
from typing import Union, Optional

from AioSpider.tools import utility_tools
from AioSpider.exceptions import SqlException, StatusTags
from AioSpider.db.sql.base import SelectBase, InsertBase, CreateTableBase, AlterTableBase, escape_strings


class MysqlSelect(SelectBase):
    MysqlFunc = (
        'ABS', 'ACOS', 'ASIN', 'ATAN', 'ATAN2', 'AVG', 'CEIL', 'CEILING',
        'COS', 'COT', 'COUNT', 'DEGREES', 'DIV', 'EXP', 'FLOOR', 'GREATEST',
        'LEAST', 'LN', 'LOG', 'LOG10', 'LOG2', 'MAX', 'MIN', 'MOD',
        'PI', 'POW', 'POWER', 'RADIANS', 'RAND', 'ROUND', 'SIGN', 'SIN',
        'SQRT', 'SUM', 'TAN', 'TRUNCATE', 'ASCII', 'CHAR_LENGTH', 'CHARACTER_LENGTH', 'CONCAT',
        'CONCAT_WS', 'FIELD', 'FIND_IN_SET', 'FORMAT', 'INSERT', 'LOCATE', 'LCASE', 'LEFT',
        'LOWER', 'LPAD', 'LTRIM', 'MID', 'POSITION', 'REPEAT', 'REPLACE', 'REVERSE',
        'RIGHT', 'RPAD', 'RTRIM', 'SPACE', 'STRCMP', 'SUBSTR', 'SUBSTRING', 'SUBSTRING_INDEX',
        'TRIM', 'UCASE', 'UPPER', 'ADDDATE', 'ADDTIME', 'CURDATE', 'CURRENT_DATE', 'CURRENT_TIME',
        'CURRENT_TIMESTAMP', 'CURTIME', 'DATE', 'DATEDIFF', 'DATE_ADD', 'DATE_FORMAT', 'DATE_SUB', 'DAY',
        'DAYNAME', 'DAYOFMONTH', 'DAYOFWEEK', 'DAYOFYEAR', 'EXTRACT', 'HOUR', 'LAST_DAY', 'LOCALTIME',
        'LOCALTIMESTAMP', 'MAKEDATE', 'MAKETIME', 'MICROSECOND', 'MINUTE', 'MONTHNAME', 'MONTH', 'NOW',
        'PERIOD_ADD', 'PERIOD_DIFF', 'QUARTER', 'SECOND', 'SEC_TO_TIME', 'STR_TO_DATE', 'SUBDATE', 'SUBTIME',
        'SYSDATE', 'TIME', 'TIME_FORMAT', 'TIME_TO_SEC', 'TIMEDIFF', 'TIMESTAMP', 'TIMESTAMPDIFF', 'TO_DAYS',
        'WEEK', 'WEEKDAY', 'WEEKOFYEAR', 'YEAR', 'YEARWEEK', 'BINARY', 'CAST',
        'COALESCE', 'CONNECTION_ID', 'CONV', 'CURRENT_USER', 'DATABASE', 'IF', 'IFNULL', 'ISNULL',
        'LAST_INSERT_ID', 'NULLIF', 'SESSION_USER', 'SYSTEM_USER', 'USER', 'VERSION'
    )

    def __str__(self):
        sql = f'SELECT {self.build_distinct()} {self.build_field()} FROM `{self._table}`'

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

        offset = self.build_offset()
        if offset:
            sql += offset

        if self._subquery:
            sql = f'SELECT {self.build_field()} FROM ({sql}) AS {self._subquery}'

        union = self.build_union()
        if union:
            sql += union

        union_all = self.build_union_all()
        if union_all:
            sql += union_all

        return sql

    def build_field(self):
        if self._field is None:
            return '*'
        elif isinstance(self._field, str):
            return self._field
        elif isinstance(self._field, (list, tuple)):
            field = []
            for i in self._field:
                if re.match(r'^(.+)\(.*\).*$', i) and re.match(
                        r'^(.+)\(.*\).*$', i).group(1).upper() in self.MysqlFunc:
                    field.append(i)
                else:
                    if re.match(r'^.* as .*$', i):
                        x, y = utility_tools.extract_with_regex(i, r'^(.*) as (.*)$')
                        field.append(f"{x} as `{y}`")
                    else:
                        field.append(f"`{i}`")
            return ",".join(field)
        else:
            raise SqlException(status=StatusTags.SqlFieldError)

    def build_order(self):
        if self._order is None:
            return None
        elif isinstance(self._order, str):
            return f' ORDER BY {self._order} {"desc" if self._desc else "asc"}'
        elif isinstance(self._order, (list, tuple)):
            return f' ORDER BY {",".join(self._order)} {"desc" if self._desc else "asc"}'
        else:
            raise SqlException(status=StatusTags.SqlOrderError)


class MysqlCreateTable(CreateTableBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_common_sql(self, field, cname, sql, default_format=None):
        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'
        elif field.unique:
            sql += f' UNIQUE'

        if field.default is not None:
            if default_format:
                sql += f' DEFAULT {default_format(field.default)}'
            else:
                sql += f' DEFAULT ' + (
                    '""' if isinstance(field.default, str) and not field.default else str(field.default)
                )

        sql += f' COMMENT "{field.name}"'
        return sql

    def build_auto_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        if field.primary:
            sql += f' NOT NULL PRIMARY KEY AUTO_INCREMENT'
        else:
            sql += f' NOT NULL AUTO_INCREMENT'
        return sql

    def build_stamp_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(field, cname, sql)
        if field.auto_update:
            sql += ' ON UPDATE CURRENT_TIMESTAMP'
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
        if field.auto_update:
            sql += ' ON UPDATE CURRENT_TIMESTAMP'
        return sql

    def __str__(self):

        cols_sql_list = self.build_cols_sql_list()
        index_sql_list = self.build_index_sql_list()
        charset = self.model.Meta.data_meta.charset

        sql = f'CREATE TABLE {self.table_name} (\n'
        sql += ',\n'.join(cols_sql_list)

        index = ',\n'.join([i for i in index_sql_list])
        if index:
            sql += f',\n{index}\n) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT="{self.model.__doc__}"'
        else:
            sql += f'\n) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT="{self.model.__doc__ or ""}"'
        print(sql)
        return sql


class MysqlAlterTable(AlterTableBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = MysqlAlterAPI(self.table_name)

    def build_add_cols_sql(self, desc):

        index = 0
        fields = list(self.model.fields.keys())
        condition = lambda cname, *args, **kwargs: cname.upper() not in [i.field.upper() for i in desc]

        def add_column_method(cname, field):
            nonlocal index
            after = fields[index - 1] if index else None
            index += 1
            return self.api.build_add_column_sql(field=field, cname=cname, after=after)

        return self.build_sql_list(add_column_method, condition)

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

    def build_modify_cols_unique_uniun_index_sql(self, indexes):

        index_fields = [i for i in self.model.Meta.union_unique_index if i in self.model.fields]
        new_index_fields = [f'`{i}`' for i in index_fields]
        index_name = f'unique_idx_{"_".join(index_fields)}'

        # 创建索引
        if index_name not in [i['name'] for i in indexes]:
            return f'CREATE UNIQUE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'

        sql = ''
        for i in indexes:
            if len(i['field']) == 1 or i['name'] != index_name:
                continue
            if set(i['field']) == set(index_fields) and i['unique']:
                continue
            sql += f'ALTER TABLE {self.model.table_name} DROP INDEX {index_name};\n'
            sql += f'CREATE UNIQUE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'

        return sql

    def build_modify_cols_uniun_index_sql(self, indexes):

        index_fields = [i for i in self.model.Meta.union_index if i in self.model.fields]
        new_index_fields = [f'`{i}`' for i in index_fields]
        index_name = f'union_idx_{"_".join(index_fields)}'

        # 创建索引
        if index_name not in [i['name'] for i in indexes]:
            return f'CREATE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'

        sql = ''
        for i in indexes:
            if len(i['field']) == 1 or i['name'] != index_name:
                continue
            if set(i['field']) == set(index_fields) and not i['unique']:
                continue
            sql += f'ALTER TABLE {self.model.table_name} DROP INDEX {index_name};\n'
            sql += f'CREATE INDEX {index_name} ON {self.model.table_name} ({", ".join(new_index_fields)});'

        return sql

    def build_modify_cols_type_sql(self, desc):

        def condition(cname, field):
            for des in desc:
                if cname.upper() == des.field.upper():
                    if field.max_length != des.length and not issubclass(field.__class__, TextField):
                        return True
                    if hasattr(field, 'unsigned'):
                        if field.unsigned and (field.mapping[self.type] + ' UNSIGNED') != des.type:
                            return True
                        if not field.unsigned and field.mapping[self.type] != des.type:
                            return True
                    else:
                        if field.mapping[self.type] == 'DECIMAL':
                            return False
                        if field.mapping[self.type] != des.type:
                            return True
                    return False
            return False
        return self.build_sql_list(self.api.build_modify_column_type_sql, condition)

    def build_drop_column_sql(self, cname: str) -> str:
        """删除列"""
        return f'ALTER TABLE `{self.table_name}` DROP COLUMN `{cname}`'

    def build_rename_column_sql(self, old_cname: str, new_cname: str) -> str:
        """重命名列"""
        field = self.model.fields[old_cname]
        sql = f'ALTER TABLE `{self.table_name}` CHANGE `{old_cname}` `{new_cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        if field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        return sql

    def build_drop_primary_key_sql(self) -> str:
        """删除主键"""
        return f'ALTER TABLE `{self.table_name}` DROP PRIMARY KEY'

    def build_drop_unique_key_sql(self, cname: str) -> str:
        """删除唯一键"""
        return f'ALTER TABLE `{self.table_name}` DROP INDEX `{cname}`'

    def build_drop_index_sql(self, cname: str) -> str:
        """删除索引"""
        return f'ALTER TABLE `{self.table_name}` DROP INDEX `{cname}`'

    def build_rename_table_sql(self, new_name: str) -> str:
        """重命名表"""
        return f'ALTER TABLE `{self.table_name}` RENAME TO `{new_name}`'

    def build_add_foreign_key_sql(
            self, cname: str, ref_table: str, ref_cname: str, on_delete: str = 'CASCADE',
            on_update: str = 'CASCADE'
    ) -> str:
        """添加外键约束"""
        return f'ALTER TABLE `{self.table_name}` ADD FOREIGN KEY (`{cname}`) REFERENCES `{ref_table}`(`' \
               f'{ref_cname}`) ON DELETE {on_delete} ON UPDATE {on_update}'

    def build_drop_foreign_key_sql(self, constraint_name: str) -> str:
        """删除外键约束"""
        return f'ALTER TABLE `{self.table_name}` DROP FOREIGN KEY `{constraint_name}`'

    def build_change_column_default_sql(self, cname: str, default_value: Union[str, int, float]) -> str:
        """更改列的默认值"""

        field = self.model.fields[cname]
        sql = f'ALTER TABLE `{self.table_name}` ALTER COLUMN `{cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        if default_value is not None:
            sql += f' DEFAULT {escape_strings(default_value)}'
        return sql

    def build_change_column_null_sql(self, cname: str, nullable: bool) -> str:
        """更改列的可空属性"""

        field = self.model.fields[cname]
        sql = f'ALTER TABLE `{self.table_name}` MODIFY COLUMN `{cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        if not nullable:
            sql += f' NOT NULL'
        if field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        return sql

    def build_change_column_charset_sql(self, cname: str, charset: str, collation: str) -> str:
        """更改列的字符集"""

        field = self.model.fields[cname]
        if field.mapping["mtype"] not in ["CHAR", "VARCHAR", "TEXT"]:
            raise SqlException(status=StatusTags.SqlFieldTypeValidatorError)
        sql = f'ALTER TABLE `{self.table_name}` MODIFY COLUMN `{cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        sql += f' CHARACTER SET {charset} COLLATE {collation}'
        if field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        return sql

    def build_change_table_storage_engine_sql(self, engine: str) -> str:
        """更改表的存储引擎"""
        return f'ALTER TABLE `{self.table_name}` ENGINE={engine}'

    def build_change_table_charset_collation_sql(self, charset: str, collation: str) -> str:
        """更改表的字符集和排序规则"""
        return f'ALTER TABLE `{self.table_name}` CONVERT TO CHARACTER SET {charset} COLLATE {collation}'

    def build_change_table_comment_sql(self, comment: str) -> str:
        """更改表的注释"""
        return f'ALTER TABLE `{self.table_name}` COMMENT="{comment}"'


class MysqlAlterAPI:

    def __init__(self, table_name):
        self.table_name = table_name

    def build_add_column_sql(self, cname: str, field, after: str = None, *args, **kwargs) -> str:

        sql = f'ALTER TABLE `{self.table_name}` ADD COLUMN `{cname}` {field.mapping["mtype"]}'

        if field.max_length is not None:
            sql += f'({field.max_length})'

        if hasattr(field, 'unsigned') and field.unsigned:
            sql += f' UNSIGNED'

        if field.primary:
            sql += f' primary key auto_increment' if field.__class__.__name__ == 'AutoIntField' else f' primary key'
        elif field.unique:
            sql += f' unique key'

        if field.mapping["mtype"] not in ['TEXT', 'BLOB', 'GEOMETRY', 'JSON'] and field.default is not None:
            if isinstance(field.default, (str, date, datetime)):
                if field.default == 'CURRENT_TIMESTAMP':
                    sql += f' DEFAULT {field.default}'
                else:
                    sql += f' DEFAULT {escape_strings(field.default)}'
            else:
                sql += f' DEFAULT {field.default}'
        else:
            sql += f' DEFAULT NULL'

        if field.name is not None:
            sql += f' COMMENT "{field.name}"'

        if after is not None:
            sql += f' AFTER {after}'

        return sql

    def build_modify_column_type_sql(self, cname: str, field, *args, **kwargs) -> str:
        # ({field.max_length}, {field.precision})
        sql = f'ALTER TABLE `{self.table_name}` MODIFY COLUMN `{cname}` {field.mapping["mtype"]}'

        if field.max_length is not None and not issubclass(field.__class__, TextField):
            sql += f'({field.max_length})'

        if hasattr(field, 'unsigned') and field.unsigned:
            sql += f' UNSIGNED'

        if field.__class__.__name__ == 'AutoIntField' and field.primary:
            sql = f'ALTER TABLE `{self.table_name}` DROP PRIMARY KEY;\n' + sql
            sql += f' AUTO_INCREMENT PRIMARY KEY'
        elif field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        else:
            sql += f' DEFAULT NULL'

        if field.name is not None:
            sql += f' COMMENT "{field.name}"'

        return sql

    def build_modify_primary_sql(self, cname: str, is_primary: bool = False, *args, **kwargs) -> str:
        if is_primary:
            return f'ALTER TABLE `{self.table_name}` DROP PRIMARY KEY;\nALTER TABLE `{self.table_name}` ADD PRIMARY' \
                   f' KEY(`{cname}`);'
        else:
            return f'ALTER TABLE `{self.table_name}` ADD PRIMARY KEY (`{cname}`);'

    def build_modify_unique_sql(self, cname: str, *args, **kwargs) -> str:
        return f'ALTER TABLE `{self.table_name}` ADD UNIQUE (`{cname}`);'

    def build_modify_index_sql(self, cname: str, *args, **kwargs) -> str:
        return f'ALTER TABLE `{self.table_name}` ADD INDEX (`{cname}`)'


class MysqlInsert(InsertBase):

    def build_insert_update_sql(self):
        sql = f'{self.build_insert_sql()} ON DUPLICATE KEY UPDATE '
        sql += ','.join([f"`{i}`=values(`{i}`)" for i in self._field])

        return sql


class MysqlUpdate:

    def __init__(self, table: str, item: dict, where: dict = None):
        self._table = table
        self._item = item
        self._where = where

    def build_update_sql(self):
        if not self._item:
            return ''

        return f'''UPDATE `{self._table}` SET {', '.join([f"`{k}` = {escape_strings(v)}" for k, v in self._item.items()])} 
        WHERE {' AND '.join([f"`{k}` = {escape_strings(v)}" for k, v in self._where.items()])};'''

    def __str__(self):
        return self.build_update_sql()

    __repr__ = __str__


class MysqlDelete:

    def __init__(self, table: str, where: dict = None):
        self._table = table
        self._where = where

    def build_delete_sql(self):

        if not self._where:
            return f'DELETE FROM {self._table}'

        where_str = utility_tools.join([f'`{k}`={escape_strings(v)}' for k, v in self._where.items()], on=' and ')

        sql = f'DELETE FROM {self._table} WHERE {where_str}'
        sql = sql.replace('None', 'NULL')

        return sql

    def __str__(self):
        return self.build_delete_sql()

    __repr__ = __str__
