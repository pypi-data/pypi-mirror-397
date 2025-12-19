from dataclasses import dataclass
from collections import OrderedDict
from functools import partial
from typing import Literal, Dict, Any, Tuple

from AioSpider import settings
from AioSpider.objects import DataBaseType, TableType, ConnectionData
from AioSpider.orm.fields import Field
from AioSpider.tools import extract_with_regex
from .query_set import QuerySet, AsyncQuerySet

__all__ = ['BaseModel', 'Model']
RType = Literal['model', 'list', 'dict', 'pd', 'iter']


@dataclass(slots=True)
class MetaDefaults:
    abstract: bool = True
    alias: str = 'DEFAULT'
    database_type: DataBaseType = None
    data_meta: ConnectionData = None
    table_name: str = None
    table_type: TableType = TableType.data
    read_only: bool = False
    base_path: str = None
    commit_size: int = 1000
    init_id: int = None
    auto_update: bool = True
    composite_indexes: Tuple[Tuple[str, ...], ...] = None
    composite_unique_indexes: Tuple[Tuple[str, ...], ...] = None
    name_type: str = None
    statistics: bool = True
    statistics_fields: Tuple[str, ...] = None
    statistics_filter: Dict[str, Any] = None


class BaseModel(type):
    """基础模型元类"""

    subclasses = set()
    meta_defaults = MetaDefaults()

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(cls, name: str, bases: Tuple, attrs: Dict[str, Any]) -> type:

        fields = cls.get_fields(bases, attrs)
        new_attrs = {k: v for k, v in attrs.items() if not isinstance(v, Field)}
        new_attrs["fields"] = fields
        new_attrs.update(fields)

        model_class = super().__new__(cls, name, bases, new_attrs)
        base_meta = getattr(bases[0], 'Meta', None) if bases else object
        meta_attrs = cls.create_meta_attrs(bases, attrs, name)
        model_class.Meta = type('Meta', (base_meta,), meta_attrs)

        def wraps_primary(cls):
            def get_primary_key():
                return [field for field, props in cls.fields.items() if props.primary]
            return get_primary_key

        def wraps_unique(cls):
            def get_unique_field():
                unique_fields = []
                if cls.Meta.composite_unique_indexes:
                    unique_fields.extend(cls.Meta.composite_unique_indexes)
                unique_fields.extend((field,) for field, props in cls.fields.items() if props.unique)
                return unique_fields
            return get_unique_field

        def wraps_index(cls):
            def get_index_field():
                index_fields = []
                if cls.Meta.composite_indexes:
                    index_fields.extend(cls.Meta.composite_indexes)
                index_fields.extend((field,) for field, props in cls.fields.items() if props.index)
                return index_fields
            return get_index_field

        cls.add_model_methods(model_class, meta_attrs)
        model_class.Meta.init_id = cls.get_init_id(model_class)

        model_class.get_primary_key = wraps_primary(model_class)
        model_class.get_unique_field = wraps_unique(model_class)
        model_class.get_index_field = wraps_index(model_class)
        model_class.make_item = cls.make_item

        cls.add_method_to_field(model_class)
        cls.subclasses.add(model_class)

        return model_class

    def __init__(cls, name: str, bases: Tuple, attrs: Dict[str, Any]):
        super().__init__(name, bases, attrs)
        cls._loaded_fields = set()      # 用于跟踪已加载的字段
        cls._data_cache = {}            # 用于缓存加载的数据

    def __call__(cls, *args, **kwargs):
        return super().__call__(*args, **kwargs)

    @classmethod
    def get_fields(cls, bases: Tuple, attrs: Dict[str, Any]) -> Dict[str, Field]:
        fields = {k: v for base in bases for k, v in getattr(base, 'fields', {}).items()}
        fields.update({k: v for k, v in attrs.items()})
        fields = ({k: v for k, v in fields.items() if isinstance(v, Field)})
        return cls.order_field(bases, attrs, fields) if fields else {}

    @classmethod
    def order_field(cls,  bases: Tuple, attrs: Dict[str, Any], fields: Dict[str, Field]) -> Dict[str, Field]:
        user_order = ('id', ) + tuple(attrs.get('order', ()))  + tuple(
            i for base in bases for i in getattr(base, 'order', ())
        ) + ('source', 'create_time', 'update_time')
        all_fields = list(dict.fromkeys(user_order + tuple(fields)))
        return {f: fields[f] for f in all_fields if f in fields}

    @classmethod
    def create_meta_attrs(cls, bases: Tuple, attrs: Dict[str, Any], name: str) -> Dict[str, Any]:
        base_meta = getattr(bases[0], 'Meta', None) if bases else None
        model_meta = attrs.get('Meta', None)

        meta_defaults = {field: getattr(cls.meta_defaults, field) for field in cls.meta_defaults.__dataclass_fields__}
        base_meta_dict = getattr(base_meta, '__dict__', {})
        model_meta_dict = getattr(model_meta, '__dict__', {})
        attrs_meta = {k: v for k, v in model_meta_dict.items() if k in cls.meta_defaults.__dataclass_fields__}

        meta_attrs = {**meta_defaults, **base_meta_dict, **model_meta_dict, **attrs_meta}
        meta_attrs['abstract'] = model_meta_dict.get('abstract', False) or attrs.get('meta', {}).get('abstract', False)
        meta_attrs['table_name'] = attrs_meta.get('table_name') or cls.get_name(name)

        return meta_attrs

    @staticmethod
    def add_method_to_field(model_cls):
        if not model_cls.fields:
            return
        for field_name, field in model_cls.fields.items():
            if hasattr(model_cls, f'validate_{field_name}'):
                new_func = partial(getattr(model_cls, f'validate_{field_name}'), self=model_cls)
                setattr(field, '_custom_validator', new_func)
            if hasattr(model_cls, f'convert_{field_name}'):
                new_func = partial(getattr(model_cls, f'convert_{field_name}'), self=model_cls)
                setattr(field, '_custom_converter', new_func)

    @staticmethod
    def get_name(name) -> str:
        name_type = settings.DataFilterConfig.MODEL_NAME_TYPE
        name = name.replace('model', '').replace('Model', '')
        if name_type == 'lower':
            return name.lower()
        elif name_type == 'upper':
            return name.upper()
        else:
            return '_'.join(i.lower() for i in extract_with_regex(pattern='[A-Z][^A-Z]*', text=name))

    def make_item(self):
        item = {}
        for k, field in self.fields.items():
            v = getattr(self, k, None)
            if field.is_saved:
                item[field.column] = v
            else:
                if self.Meta.database_type == DataBaseType.sqlite and hasattr(field, 'auto_now') and field.auto_now:
                    item[field.column] = v
        return item

    @staticmethod
    def add_model_methods(model_class, meta_attrs):
        model_class.table_name = meta_attrs['table_name']
        model_class.objects = QuerySet.from_model(model_class) if not meta_attrs['abstract'] and meta_attrs['database_type'] else None
        model_class.async_objects = None

    @staticmethod
    def get_init_id(model_class):
        if model_class.objects is None:
            return 1
        try:
            max_id = model_class.objects.max('id')
            return max_id + 1 if max_id else 1
        except Exception:
            return None


class Model(metaclass=BaseModel):

    def __init__(self, **kwargs):
        self._values = {}
        self._initialize_fields(kwargs)

    def _initialize_fields(self, data):
        cleaned_data = self.clean(data) or data
        fields = [i.column for i in self.fields.values()]
        for field_name, value in cleaned_data.items():
            if field_name not in self.fields and field_name not in fields:
                raise AttributeError(f"字段 '{field_name}' 在 {self.__class__.__name__} 中不存在")
            setattr(self, field_name, value)

    @classmethod
    async def apply_async(cls):
        cls.async_objects = await AsyncQuerySet.from_model(cls)

    @classmethod
    @property
    def database(cls):
        return cls.Meta.data_meta.db if cls.Meta.data_meta else None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def get(cls, **kwargs):
        return cls.objects.filter(**kwargs).get()

    def clean(self, item):
        return item

    def spider_close(self, spider):
        pass

    def save(self):
        item = self.make_item()
        query_set = self.objects.filter(**{
            field: item[field] for fields in self.__class__.get_unique_field() for field in fields
        })
        if query_set.exists():
            return self.objects.update_filter(**{
                field: item[field] for fields in self.__class__.get_unique_field() for field in fields
            }).update(**item)
        return self.objects.create(**item)

    @classmethod
    def filter(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self.objects.update_filter(id=self.id).update(**{k: getattr(self, k) for k in kwargs})

    @classmethod
    def get_data_length(cls):
        pass

    @classmethod
    def get_index_length(cls):
        pass

    @classmethod
    def get_last_update(cls):
        pass

    @classmethod
    def check_table_exists(cls):
        """检查表是否存在"""
        pass

    @classmethod
    def get_column_info(cls):
        """获取表的列信息"""
        pass

    @classmethod
    def get_table_size(cls):
        """获取表的大小（以字节为单位）"""
        pass

    @classmethod
    def get_auto_increment_value(cls) -> int:
        """获取自增列的当前值"""
        pass

    @classmethod
    def get_index_info(cls):
        """获取索引信息"""
        pass

    @classmethod
    def get_table_ddl(cls) -> str:
        """获取表的DDL（数据定义语言）"""
        pass

    @classmethod
    def get_total_rows(cls):
        pass

    @classmethod
    def get_duplicate_rows(cls, column_name):
        """获取指定列的重复行"""
        pass

    @classmethod
    def get_null_rows(cls, column_name) -> int:
        """获取指定列的空值行数"""
        pass

    @classmethod
    def get_zero_count(cls, column_name) -> int:
        """获取指定列的零值行数"""
        pass

    @classmethod
    def get_distinct_count(cls, column_name) -> int:
        """获取指定列的不同值数量"""
        pass

    @classmethod
    def get_column_data_distribution(cls, column_name, desc=False, limit=None):
        """获取指定列的数据分布"""
        pass

    @classmethod
    def get_length(cls, column_name):
        """获取指定列的长度"""
        pass

    @classmethod
    def get_avg_length(cls, column_name):
        """获取指定列的平均长度"""
        pass

    @classmethod
    def get_max_length(cls, column_name):
        """获取指定列的最大长度"""
        pass

    @classmethod
    def get_min_length(cls, column_name):
        """获取指定列的最小长度"""
        pass
