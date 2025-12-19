from typing import Literal

import aiofiles
from pandas import DataFrame

from AioSpider.objects import WriteMode, DataBaseType
from AioSpider.orm.fields import (
    AutoIntField,
    BlobField,
    CharField,
    DateTimeField,
    ExtensionNameField,
    PathField,
)
from ..builder.aggregates import Count, Avg, Min, Max, Distinct, Sum, Std, Variance, Length
from ..builder.fields_conditions import F

from .base_model import Model, BaseModel

__all__ = [
    'ABCModel', 
    'SQLiteModel', 
    'MySQLModel',
    'MariaDBModel',
    'PostgreSQLModel',
    'OracleModel',
    'SQLServerModel',
    'MongoModel',
    'FileModel',
    'CSVModel',
    'RedisModel'
]

RType = Literal['model', 'list', 'dict', 'pd', 'iter']


class ABCModel(Model):
    class Meta:
        abstract = True

    id = AutoIntField(name='主键', primary=True, is_saved=False)
    source = CharField(name='数据源', max_length=20)
    create_time = DateTimeField(name='创建时间', null=False, auto_add=True, is_saved=False)
    update_time = DateTimeField(name='更新时间', null=False, auto_add=True, auto_now=True, is_saved=False)


class SQLiteModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.sqlite

    @classmethod
    def get_data_length(cls):
        """获取表的数据长度"""
        return cls.objects.only(Count()).get(flat=True) or 0

    @classmethod
    def get_index_length(cls):
        """获取索引长度"""
        # SQLite不直接支持获取索引长度，可以返回索引数量作为替代
        return len(cls.get_index_info())

    @classmethod
    def get_last_update(cls):
        """获取最后更新时间"""
        return cls.objects.order_by('-update_time').only('update_time').get(flat=True) or None

    @classmethod
    def check_table_exists(cls):
        """检查表是否存在"""
        result = cls.objects.fetch(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{cls.table_name}'")
        return True if result and result[0] else False

    @classmethod
    def get_column_info(cls):
        """获取表的列信息"""
        return cls.objects.fetch(f"PRAGMA table_info(`{cls.table_name})`")

    @classmethod
    def get_table_size(cls):
        """获取表的大小（以字节为单位）"""
        # SQLite不直接支持获取表大小，可以返回行数作为替代
        return cls.get_total_rows()

    @classmethod
    def get_auto_increment_value(cls) -> int:
        """获取自增列的当前值"""
        # SQLite使用rowid作为自增列
        return cls.objects.order_by('-id').only('id').get(flat=True) or None

    @classmethod
    def get_index_info(cls):
        """获取索引信息"""
        return cls.objects.fetch(f"PRAGMA index_list(`{cls.table_name}`)")

    @classmethod
    def get_table_ddl(cls) -> str:
        """获取表的DDL（数据定义语言）"""
        result = cls.objects.fetch(f"SELECT sql FROM sqlite_master WHERE type='table' AND name={cls.table_name}")
        return result[0].get('sql', '') if result else None

    @classmethod
    def get_total_rows(cls):
        return cls.objects.only(Count()).get(flat=True) or 0

    @classmethod
    def get_duplicate_rows(cls, column_name):
        """获取指定列的重复行"""
        return cls.objects.only(column_name, Count()).group_by(column_name).having(F(Count()) > 1).all()

    @classmethod
    def get_null_rows(cls, column_name) -> int:
        """获取指定列的空值行数"""
        return cls.filter(**{column_name + '__isnull': True}).only(Count()).get(flat=True) or 0
    
    @classmethod
    def get_zero_count(cls, column_name) -> int:
        """获取指定列的零值行数"""
        return cls.filter(**{column_name: 0}).only(Count()).get(flat=True) or 0

    @classmethod
    def get_distinct_count(cls, column_name) -> int:
        """获取指定列的不同值数量"""
        return cls.objects.only(Count(Distinct(column_name))).get(flat=True) or 0

    @classmethod
    def get_column_data_distribution(cls, column_name, desc=False, limit=None):
        """获取指定列的数据分布"""
        queryset = cls.objects.only(
                column_name, Count(column_name)
            ).group_by(column_name).order_by('-' + column_name if desc else column_name)
        if limit is not None:
            queryset = queryset.limit(limit)
        return queryset.all()
    
    @classmethod
    def get_null_rate(cls, column_name):
        """获取指定列的空值比例"""
        total_rows = cls.get_total_rows()
        if total_rows == 0:
            return 0
        return cls.get_null_rows(column_name) / total_rows
    
    @classmethod
    def get_unique_rate(cls, column_name):
        """获取指定列的不同值比例"""
        total_rows = cls.get_total_rows()
        if total_rows == 0:
            return 0
        return cls.get_distinct_count(column_name) / total_rows
    
    @classmethod
    def get_max_length(cls, column_name):
        """获取指定列的最大长度"""
        return cls.objects.only(Max(Length(column_name))).get(flat=True) or None
    
    @classmethod
    def get_min_length(cls, column_name):
        """获取指定列的最小长度"""
        return cls.objects.only(Min(Length(column_name))).get(flat=True) or None
    
    @classmethod
    def get_avg_length(cls, column_name):
        """获取指定列的平均长度"""
        return cls.objects.only(Avg(Length(column_name))).get(flat=True) or None


class MySQLModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.mysql

    @classmethod
    def get_data_length(cls):
        result = cls.objects.fetch(f'''
        SELECT 
            data_length
        FROM 
            information_schema.tables
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}'; 
        ''')
        return result[0].get('data_length', 0) if result else 0

    @classmethod
    def get_index_length(cls):
        result =  cls.objects.fetch(f'''
        SELECT 
            index_length
        FROM 
            information_schema.tables
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}'; 
        ''')
        return result[0].get('index_length', 0) if result else 0

    @classmethod
    def get_last_update(cls):
        result = cls.objects.fetch(f'''
        SELECT 
            update_time
        FROM 
            information_schema.tables
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}'; 
        ''')
        return result[0].get('update_time', None) if result else None

    @classmethod
    def check_table_exists(cls):
        """检查表是否存在"""
        result = cls.objects.fetch(f'''
        SELECT 
            COUNT(*) AS table_exists
        FROM 
            information_schema.tables
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}';
        ''')
        return (result[0].get('table_exists', 0) if result else 0) > 0

    @classmethod
    def get_column_info(cls):
        """获取表的列信息"""
        return cls.objects.fetch(f'''
        SELECT 
            COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM 
            information_schema.columns
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}';
        ''')

    @classmethod
    def get_table_size(cls):
        """获取表的大小（以字节为单位）"""
        result =  cls.objects.fetch(f'''
        SELECT 
            data_length + index_length AS table_size
        FROM 
            information_schema.tables
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}';
        ''')
        return result[0].get('table_size', 0) if result else 0

    @classmethod
    def get_auto_increment_value(cls) -> int:
        """获取自增列的当前值"""
        result = cls.objects.fetch(f'''
        SELECT 
            AUTO_INCREMENT
        FROM 
            information_schema.tables
        WHERE 
            table_name = '{cls.table_name}' and table_schema = '{cls.database}';
        ''')
        return result[0].get('AUTO_INCREMENT', 1) if result else 1

    @classmethod
    def get_index_info(cls):
        """获取索引信息"""
        return cls.objects.fetch(f'''SHOW INDEX FROM `{cls.table_name}`;''')

    @classmethod
    def get_table_ddl(cls) -> str:
        """获取表的DDL（数据定义语言）"""
        result = cls.objects.fetch(f'''SHOW CREATE TABLE `{cls.table_name}`;''')
        return result[0].get('Create Table') if result else None

    @classmethod
    def get_total_rows(cls):
        return cls.objects.only(Count()).get(flat=True) or 0

    @classmethod
    def get_duplicate_rows(cls, column_name):
        """获取指定列的重复行"""
        return cls.objects.only(column_name, Count()).group_by(column_name).having(F(Count()) > 1).all()

    @classmethod
    def get_null_rows(cls, column_name) -> int:
        """获取指定列的空值行数"""
        return cls.filter(**{column_name + '__isnull': True}).only(Count()).get(flat=True) or 0

    @classmethod
    def get_distinct_count(cls, column_name) -> int:
        """获取指定列的不同值数量"""
        return cls.objects.only(Count(Distinct(column_name))).get(flat=True) or 0

    @classmethod
    def get_column_data_distribution(cls, column_name, desc=False, limit=None):
        """获取指定列的数据分布"""
        queryset = cls.objects.only(
                column_name, Count(column_name)
            ).group_by(column_name).order_by('-' + column_name if desc else column_name)
        if limit is not None:
            queryset = queryset.limit(limit)
        return queryset.all()
    
    @classmethod
    def get_null_rate(cls, column_name):
        """获取指定列的空值比例"""
        total_rows = cls.get_total_rows()
        if total_rows == 0:
            return 0
        return cls.get_null_rows(column_name) / total_rows
    
    @classmethod
    def get_unique_rate(cls, column_name):
        """获取指定列的不同值比例"""
        total_rows = cls.get_total_rows()
        if total_rows == 0:
            return 0
        return cls.get_distinct_count(column_name) / total_rows
    
    @classmethod
    def get_max_length(cls, column_name):
        """获取指定列的最大长度"""
        return cls.objects.only(Max(Length(column_name))).get(flat=True) or None

    @classmethod
    def get_min_length(cls, column_name):
        """获取指定列的最小长度"""
        return cls.objects.only(Min(Length(column_name))).get(flat=True) or None
    
    @classmethod
    def get_avg_length(cls, column_name):
        """获取指定列的平均长度"""
        return cls.objects.only(Avg(Length(column_name))).get(flat=True) or None


class PostgreSQLModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.postgresql


class MariaDBModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.mariadb


class OracleModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.oracle


class SQLServerModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.sqlserver


class MongoModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.mongodb


class FileModel(ABCModel):
    class Meta:
        abstract = True
        mode = 'wb'  # 文件打开模式
        database_type = DataBaseType.file  # 文件存储引擎

    name = CharField(name='文件名', max_length=255)
    path = PathField(name='文件夹路径', max_length=255)
    extension = ExtensionNameField(name='拓展名')
    content = BlobField(name='内容')

    order = [
        'name', 'path', 'extension', 'content', 'source', 'create_time', 'update_time'
    ]

    def __init__(
            self, name=None, path=None, extension=None, content=None, extract: bool = False,
            related=None, **kwargs
    ):
        self.extract = extract
        self.related = related
        super(FileModel, self).__init__(
            name=name, path=path, extension=extension, content=content, **kwargs
        )

    async def save(self):

        if self.Meta.mode in ['w', 'w+', 'a', 'a+'] and isinstance(self.content, bytes):
            content = self.content.decode(self.Meta.data_meta.charset)
        elif self.Meta.mode in ['wb', 'wb+', 'ab', 'ab+'] and isinstance(self.content, str):
            content = self.content.encode(self.Meta.data_meta.charset)
        else:
            content = self.content

        if self.path is None:
            path = self.Meta.base_path
        else:
            path = self.Meta.base_path / str(self.path)

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        if self.Meta.mode in ['wb', 'wb+', 'ab', 'ab+']:
            fopen = aiofiles.open(str(path / (self.name + self.extension)), self.Meta.mode)
        else:
            fopen = aiofiles.open(
                str(path / (self.name + self.extension)), self.Meta.mode, encoding=self.Meta.data_meta.charset
            )

        try:
            async with fopen as fp:
                await fp.write(self.content)
        except OSError:
            print(f'{str(self.path / (self.name + self.extension))}：文件路径中有特殊字符，请手动处理')

        file_path = path / (self.name + self.extension)

        if self.extract:
            return self.extract_table(file_path)

        return file_path

    def extract_table(self, path):
        return None

    def process_dataframe(self, df):

        if self.related is None:
            return df

        clos = df.columns.tolist()
        if type(self.related) is BaseModel:
            fields = self.related.fields
        elif isinstance(self.related, list):
            fields = {}
            for i in self.related:
                if not issubclass(i, Model):
                    continue
                fields.update(i.fields)
        elif isinstance(self.related, dict):
            fields = {}
            for k, v in self.related.items():
                if not issubclass(v, Model):
                    continue
                fields.update(v.fields)
        else:
            fields = {}

        for k, v in fields.items():
            if v.name not in clos:
                continue
            for idx, i in enumerate(clos):
                if i != v.name:
                    continue
                df[i].fillna(v.mapping['ftype'](), inplace=True)
                clos[idx] = k

        df.columns = clos

        return df

    def process_raw_dataframe(self, df: DataFrame) -> DataFrame:
        return df

    def process_item(self, item: dict):
        return item

    def yield_dataframe(self, df: DataFrame):
        for index, row in df.T.items():
            item = self.process_item(row.to_dict())
            if item is None:
                continue
            if isinstance(item, Model):
                yield item
            elif isinstance(item, dict):
                yield self.related(item)
            elif hasattr(item, '__iter__'):
                for i in item:
                    if i is None:
                        continue
                    if isinstance(i, Model):
                        yield i
                    elif isinstance(item, dict):
                        yield self.related(item)


class CSVModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.csv
        write_mode = WriteMode.A


class RedisModel(ABCModel):
    class Meta:
        abstract = True
        database_type = DataBaseType.redis
        data_type = 'hash'
