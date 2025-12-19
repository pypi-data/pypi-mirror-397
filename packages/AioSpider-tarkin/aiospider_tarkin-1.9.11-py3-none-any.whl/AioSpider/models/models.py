from collections import namedtuple
from datetime import datetime
from typing import Union, Optional, Literal, Dict, Any, Tuple, Type

import aiofiles
from pandas import DataFrame

from AioSpider import logger
from AioSpider import field
from AioSpider import settings
from AioSpider.constants import WriteMode, DataBaseMode, DataBaseType
from AioSpider.exceptions import DatabaseException, StatusTags
from AioSpider.tools.string_tools import re
from AioSpider.tools.file_tools import mkdir
from AioSpider.db import SyncMySQLAPI, SyncSQLiteAPI, SyncMongoAPI, SyncRdisAPI, AsyncCSVFile, Connector

from .query_set import QuerySet


RType = Literal['model', 'list', 'dict', 'pd', 'iter']


class ModelConnector:

    databases: Optional[Dict[str, Any]] = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, engine: Optional[str] = None, db: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.db = db
        self.config = config

    @property
    def connector(self) -> Any:

        assert self.config is not None, DatabaseException(status=StatusTags.LodingConfigError)

        if self.databases is None:
            self.databases = self.init_database()

        return self.databases[self.engine][self.db]

    def init_database(self) -> Dict[str, Any]:

        conn_dict = dict()

        # SQLite
        if self.config.get(DataBaseMode.sqlite) and self.config[DataBaseMode.sqlite]['enabled']:
            conn_dict[DataBaseType.sqlite] = self.init_sqlite()

        # CSV
        if self.config.get(DataBaseMode.csv) and self.config[DataBaseMode.csv]['enabled']:
            conn_dict[DataBaseType.csv] = self.init_csv()

        # MySQL
        if self.config.get(DataBaseMode.mysql) and self.config[DataBaseMode.mysql]['enabled']:
            conn_dict[DataBaseType.mysql] = self.init_mysql()

        # MongoDB
        if self.config.get(DataBaseMode.mongo) and self.config[DataBaseMode.mongo]['enabled']:
            conn_dict[DataBaseType.mongo] = self.init_mongo()

        # File
        if self.config.get(DataBaseMode.file) and self.config[DataBaseMode.file]['enabled']:
            conn_dict[DataBaseType.file] = self.init_file()

        # Redis
        if self.config.get(DataBaseMode.redis) and self.config[DataBaseMode.redis]['enabled']:
            conn_dict[DataBaseType.redis] = self.init_redis()

        return conn_dict

    def init_sqlite(self):

        sq_conf = self.config[DataBaseMode.sqlite]['CONNECT']
        sqlite_conn = Connector()

        for name, config in sq_conf.items():

            sq_path = config['SQLITE_PATH'] / config['SQLITE_DB']
            sq_timeout = config['SQLITE_TIMEOUT']

            if not sq_path.exists():
                mkdir(sq_path)

            sqlite_conn[name] = SyncSQLiteAPI(path=sq_path, timeout=sq_timeout)

        return sqlite_conn

    def init_csv(self):

        csv_conf = self.config[DataBaseMode.csv]['CONNECT']
        csv_conn = Connector()

        for name, config in csv_conf.items():

            csv_path = config['CSV_PATH']
            encoding = config['ENCODING']

            if not csv_path.exists():
                mkdir(csv_path)

            csv_conn[name] = AsyncCSVFile(path=csv_path, encoding=encoding)

        return csv_conn

    def init_mysql(self):

        mysql_conf = self.config[DataBaseMode.mysql]['CONNECT']
        mysql_conn = Connector()

        for name, config in mysql_conf.items():

            host = config['MYSQL_HOST']
            port = config['MYSQL_PORT']
            db = config['MYSQL_DB']
            user = config['MYSQL_USER_NAME']
            pwd = config['MYSQL_USER_PWD']
            charset = config['MYSQL_CHARSET']
            timeout = config['MYSQL_CONNECT_TIMEOUT']
            time_zone = config['MYSQL_TIME_ZONE']

            mysql_conn[name] = SyncMySQLAPI(
                host=host, port=port, db=db, user=user, password=pwd,
                connect_timeout=timeout, charset=charset, time_zone=time_zone
            )

        return mysql_conn

    def init_mongo(self):

        mongo_conf = self.config[DataBaseMode.mongo]['CONNECT']
        mongo_conn = Connector()

        for name, config in mongo_conf.items():
            mo_host = config['MONGO_HOST']
            mo_port = config['MONGO_PORT']
            mo_db = config['MONGO_DB']
            mo_auth_db = config['MONGO_AUTH_DB']
            mo_user = config['MONGO_USERNAME']
            mo_pwd = config['MONGO_PASSWORD']

            mongo_conn[name] = SyncMongoAPI(
                host=mo_host, port=mo_port, db=mo_db, auth_db=mo_auth_db, username=mo_user, password=mo_pwd
            )

        return mongo_conn

    def init_file(self):

        file_conf = self.config[DataBaseMode.file]['CONNECT']
        file_conn = Connector()

        for name, config in file_conf.items():

            file_path = config['FILE_PATH']

            if not file_path.exists():
                mkdir(file_path)

            file_conn[name] = config

        return file_conn

    def init_redis(self):

        redis_conf = self.config[DataBaseMode.redis]['CONNECT']
        redis_conn = Connector()

        for name, config in redis_conf.items():
            redis_conn[name] = SyncRdisAPI(**config)

        return redis_conn

    def get_config(self) -> Optional[Dict[str, Any]]:

        default_sts = {
            k: v for k, v in getattr(settings, 'DataBaseConfig').__dict__.items()
            if (not k.startswith('__') or not k.endswith('__')) and v.get('enabled')
        }

        try:
            from importlib import import_module
            sts = __import__('settings')
        except Exception:
            logger.warning('当前项目未找到 settings.py 配置文件')
            return default_sts

        if sts is not None and hasattr(sts, 'DataBaseConfig'):
            default_sts.update({
                k: v for k, v in getattr(sts, 'DataBaseConfig').__dict__.items()
                if not k.startswith('__') or not k.endswith('__')
            })

        return default_sts

    def __get__(self, instance: Any, owner: Type[Any]) -> Union[Any, 'ModelConnector']:

        if isinstance(self, owner):
            return self

        assert owner.Meta.engine is not None, DatabaseException(status=StatusTags.MissingEngineError)

        ins = self.__class__(
            engine=owner.Meta.engine, db=owner.Meta.db, config=owner.Meta.config or self.get_config()
        )

        return ins.connector


class BaseModel(type):
    """
    基础模型元类
    """

    _MetaDefaults = namedtuple('MetaDefaults', [
        'abstract', 'encoding', 'write_mode', 'commit_size', 'engine', 'db', 'tb_name', 'config',
        'init_id', 'read_only', 'auto_update', 'union_index', 'union_unique_index', 'base_path',
        'name_type', 'data_type'
    ])

    meta_defaults: _MetaDefaults = _MetaDefaults(
        abstract=True, encoding=None, write_mode=None, commit_size=1000, engine=None,  db='DEFAULT', tb_name=None,
        config=None, init_id=None, read_only=False, auto_update=True, union_index=None, union_unique_index=None,
        base_path=None, name_type=None, data_type='string'
    )

    def __new__(cls, name: str, bases: Tuple, attrs: Dict[str, Any]) -> type:
        """
        创建新类
        """

        # 获取父类的所有字段
        fields = {k: v for base in bases for k, v in getattr(base, 'fields', {}).items()}
        fields = cls.overwrite_fields(fields, attrs)

        # 过滤掉新类中与父类重复的字段
        new_attrs = {
            k: v for k, v in attrs.items() if not (
                isinstance(v, field.Field) and fields.setdefault(k, v)
            )
        }

        # 排序字段，确保字段顺序
        if fields:
            fields = cls.order_field(new_attrs, fields)

        # 添加新类字段
        new_attrs["fields"] = fields
        new_attrs.update(fields)
        model_class = super().__new__(cls, name, bases, new_attrs)

        # 创建 Meta 类
        base_meta = getattr(bases[0], 'Meta', None) if bases else None
        model_meta = attrs.get('Meta', None)

        # 合并元类属性
        meta_attrs = {
            **cls.meta_defaults._asdict(),
            **getattr(base_meta, '__dict__', {}),
            **getattr(model_meta, '__dict__', {}),
            **{k: v for k, v in attrs.get('meta', {}).items() if k in cls.meta_defaults._fields}
        }

        # 设置 abstract 属性
        meta_attrs['abstract'] = False
        if getattr(model_meta, '__dict__', {}).get('abstract'):
            meta_attrs['abstract'] = True

        if attrs.get('meta', {}).get('abstract'):
            meta_attrs['abstract'] = True

        if meta_attrs['abstract']:
            meta_attrs['__abstractmethods__'] = frozenset(['__str__', '__repr__'])

        if not hasattr(model_meta, 'tb_name'):
            meta_attrs['tb_name'] = cls.get_name(name)

        # 创建 Meta 类并添加到新类中
        model_class.Meta = type('Meta', (base_meta or object,), meta_attrs)

        return model_class

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        obj.__class__ = cls
        return obj

    @classmethod
    def order_field(cls, attrs: Dict[str, Any], fields: Dict[str, field.Field]) -> Dict[str, field.Field]:

        if 'order' in attrs:
            order = ['id'] + list(attrs.pop('order', [])) + ['source', 'create_time', 'update_time']
            ordered_fields = list(dict.fromkeys(order + list(fields.keys())))
        else:
            ordered_fields = list(fields.keys())

        for i in ordered_fields[:]:

            if i not in fields or not isinstance(fields[i], field.HashField):
                continue

            make_hash_field = fields[i].make_hash_field

            if make_hash_field is None:
                # 将没有指定哈希字段的字段移到最后
                ordered_fields.remove(i)
                ordered_fields.append(i)
            elif isinstance(make_hash_field, (str, field.Field)):
                # 处理哈希字段为字符串或字段对象的情况
                x = next((k for k, v in fields.items() if v is make_hash_field), '')
                if x and x in ordered_fields and ordered_fields.index(i) < ordered_fields.index(x):
                    # 将当前字段移到哈希字段之后
                    ordered_fields.remove(i)
                    ordered_fields.insert(ordered_fields.index(x) + 1, i)
            elif isinstance(make_hash_field, (tuple, list)):
                # 处理哈希字段为元组或列表的情况
                max_index = max(
                    ordered_fields.index(k) if isinstance(k, str) else ordered_fields.index(k) for x in make_hash_field
                    for k, v in fields.items() if v is x or k is x
                )
                if ordered_fields.index(i) < max_index:
                    # 将当前字段移到哈希字段集合中最后一个字段之后
                    ordered_fields.remove(i)
                    ordered_fields.insert(max_index + 1, i)

        return {k: fields[k] for k in ordered_fields if k in fields}

    @classmethod
    def overwrite_fields(cls, fields: Dict[str, Any], attrs: Dict[str, Any]) -> Dict:
        fields.update({k: v for k, v in attrs.items() if isinstance(v, field.Field) or k in fields})
        return {k: v for k, v in fields.items() if v is not None}

    @classmethod
    def get_name(cls, name) -> str:

        from AioSpider import settings
        name_type = settings.DataFilterConfig.MODEL_NAME_TYPE

        if name_type == 'lower':
            return name.lower().replace('model', '')
        elif name_type == 'upper':
            return name.upper().replace('MODEL', '')
        else:
            name = name.replace('model', '').replace('Model', '')
            name = re(regx='[A-Z][^A-Z]*', text=name)
            name = [i.lower() for i in name]
            return '_'.join(name)


class Model(metaclass=BaseModel):

    database = ModelConnector()
    objects = QuerySet()

    def __init__(self, *args, **kwargs):

        item = args[0] if args and isinstance(args[0], dict) else kwargs

        self.create_time = datetime.now()
        self.update_time = datetime.now()

        item = self.clean(item)

        for k in self.fields:
            if k not in item:
                continue
            setattr(self, k, item[k])

    @classmethod
    def get_unique_field(cls, include_id=False):

        unique_fields = list(cls.Meta.union_unique_index or [])
        [unique_fields.append(field) for field, props in cls.fields.items() if props.unique]
        if not include_id and 'id' in unique_fields:
            unique_fields.remove('id')
        unique_fields = sorted(unique_fields, key=lambda field: list(cls.fields.keys()).index(field))
        return unique_fields

    def make_item(self):

        item = {}

        for k, v in self.fields.items():
            if not v.is_save:
                continue
            if self.Meta.engine == DataBaseType.mysql:
                if isinstance(v, field.DateTimeField) and v.auto_add:
                    continue
                item[k] = getattr(self, k, None)
            else:
                item[k] = getattr(self, k, None)

        if 'id' in item:
            item.pop('id')

        return item

    def clean(self, item):
        return item

    def verify(self):
        pass

    def save(self):
        self.id = self.create(**self.make_item())
        data = self.objects.get(id=self.id)
        for field in self.fields:
            if field not in data:
                continue
            setattr(self, field, data[field])

    @classmethod
    def filter(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def creates(cls, items):
        return cls.objects.creates(items)

    def delete(self):
        return self.objects.delete()

    def update(self):
        item = {k: v for k, v in self.make_item().items() if v}
        self.objects.update(items=item, where='id')
    
    @classmethod
    @property
    def tb_name(cls):
        return cls.Meta.tb_name

    def __str__(self):
        return f'{self.__class__.__name__} {self.id}'

    __repr__ = __str__


class ABCModel(Model):
    
    class Meta:
        abstract = True

    id = field.AutoIntField(name='主键', primary=True)
    source = field.CharField(name='数据源', max_length=50)
    create_time = field.DateTimeField(name='创建时间', auto_add=True)
    update_time = field.DateTimeField(name='更新时间', auto_add=True, auto_update=True)


class SQLiteModel(ABCModel):

    class Meta:
        engine = DataBaseType.sqlite


class MySQLModel(ABCModel):

    class Meta:
        engine = DataBaseType.mysql
        
        
class MongoModel(ABCModel):

    class Meta:
        engine = DataBaseType.mongo


class FileModel(ABCModel):

    class Meta:
        encoding = 'utf-8'             # 文件编码格式
        mode = 'wb'                    # 文件打开模式
        engine = DataBaseType.file     # 文件存储引擎

    name = field.CharField(name='文件名', max_length=255)
    path = field.PathField(name='文件夹路径', max_length=255)
    extension = field.ExtensionNameField(name='拓展名')
    content = field.BytesContentField(name='内容')

    order = [
        'name', 'path', 'extension', 'content', 'source', 'create_time', 'update_time'
    ]

    def __init__(
            self, name=None, path=None, extension=None, content=None, extract: bool = False, 
            related=None, *args, **kwargs
    ):
        self.extract = extract
        self.related = related
        super(FileModel, self).__init__(
            name=name, path=path, extension=extension, content=content, *args, **kwargs
        )

    async def save(self):

        if self.Meta.mode in ['w', 'w+', 'a', 'a+'] and isinstance(self.content, bytes):
            content = self.content.decode(self.Meta.encoding)
        elif self.Meta.mode in ['wb', 'wb+', 'ab', 'ab+'] and isinstance(self.content, str):
            content = self.content.encode(self.Meta.encoding)
        else:
            content = self.content
        
        if self.path is None:
            path = self.Meta.base_path
        else:
            path = self.Meta.base_path / str(self.path)

        if not path.exists():
            mkdir(path)

        if self.Meta.mode in ['wb', 'wb+', 'ab', 'ab+']:
            fopen = aiofiles.open(
                str(path / (self.name + self.extension)), self.Meta.mode
            )
        else:
            fopen = aiofiles.open(
                str(path / (self.name + self.extension)), self.Meta.mode, encoding=self.Meta.encoding
            )

        try:
            async with fopen as fp:
                await fp.write(self.content)
        except OSError:
            logger.error(f'{str(self.path / (self.name + self.extension))}：文件路径中有特殊字符，请手动处理')
            
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
                    else:
                        raise DatabaseException(status=StatusTags.DataReturnTypeError)
            else:
                raise DatabaseException(status=StatusTags.DataReturnTypeError)


class CSVModel(ABCModel):

    class Meta:
        engine = 'csv'
        encoding = 'utf-8'
        write_mode = WriteMode.A


class RedisModel(ABCModel):

    class Meta:
        engine = DataBaseType.redis
        data_type = 'hash'
