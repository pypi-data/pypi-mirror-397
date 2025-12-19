__all__ = ['LoadModels']

import sys
from importlib import import_module
from typing import List, Type

from AioSpider.orm import models, AsyncQuerySet, QuerySet
from AioSpider.objects import DataBaseType, TableType
from AioSpider.exceptions import SettingsConfigException


class LoadModels:
    """
    加载模型类
    """

    def __init__(self, spider, db_config):
        self.spider = spider
        self.db_config = db_config
        self.models: List[Type[models.Model]] = []

    async def initialize(self) -> List[Type[models.Model]]:
        """
        初始化模型类
        """
        self._load_spider_models()
        self._load_builtin_models()
        await self._add_async_queryset()
        return self.models

    def _load_spider_models(self):
        """
        加载爬虫模块中所有非抽象类的模型
        """
        spider_module = sys.modules[self.spider.__module__]
        global_namespace = vars(spider_module)

        self.models = [
            obj for name, obj in global_namespace.items()
            if (isinstance(obj, type) and
                issubclass(obj, models.Model) and
                obj != models.Model and
                not getattr(obj.Meta, 'abstract', False))
        ]

        for model in self.models:
            connects_data = getattr(self.db_config, model.Meta.database_type.value, {}).connect
            for i in connects_data:
                if model.Meta.alias == i.alias:
                    model.Meta.data_meta = i
            if model.Meta.data_meta is None:
                raise SettingsConfigException(f'无法为 {model} 配置 {model.Meta.database_type.value} 数据库配置连接对象')
            if model.Meta.database_type == DataBaseType.file:
                for i in connects_data:
                    if model.Meta.alias == i.alias:
                        model.Meta.base_path = i.path
            else:
                model.Meta.base_path = ''

    def _update_model_bases(self, model: Type[models.Model], db_type: DataBaseType):
        base_models = {
            DataBaseType.sqlite: models.SQLiteModel,
            DataBaseType.mysql: models.MySQLModel,
            DataBaseType.csv: models.CSVModel,
            DataBaseType.file: models.FileModel,
            DataBaseType.mongodb: models.MongoModel,
            DataBaseType.redis: models.RedisModel
        }

        if db_type not in base_models:
            raise SettingsConfigException(f'{model.Meta.alias} ORM 类型配置错误')

        base_model = base_models[db_type]
        
        # 检查base_model是否在model的继承链中
        if not issubclass(model, base_model):
            # 如果不在，则添加base_model到继承链中
            model.__bases__ = (base_model,) + model.__bases__
            model.Meta.database_type = db_type

        # 更新Meta类
        # model.Meta = type(
        #     'Meta', (model.Meta,), {
        #         k: v for k, v in base_model.Meta.__dict__.items()
        #         if v is not None and k not in ('table_name', 'table_type')
        #     }
        # )

        if model.objects is None:
            model.objects = QuerySet.from_model(model)

        if model in self.models:
            self.models.remove(model)

        self.models.insert(0, model)

    def _load_builtin_models(self):

        custom_models = self._load_custom_models()
        builtin_models = self._load_default_builtin_models(custom_models)

        for model in custom_models + builtin_models:
            self._update_model_bases(model, model.Meta.database_type or DataBaseType.sqlite)
            connects_data = getattr(self.db_config, model.Meta.database_type.value, {}).connect
            for i in connects_data:
                if model.Meta.alias == i.alias:
                    model.Meta.data_meta = i
            if model.Meta.data_meta is None:
                raise SettingsConfigException(f'无法为 {model} 配置 {model.Meta.database_type.value} 数据库配置连接对象')

    def _is_valid_model(self, model):
        return (
            isinstance(model, type) and issubclass(model, models.Model) and
            not model.Meta.abstract and model.Meta.table_type != TableType.data
        )

    def _load_custom_models(self) -> List[Type[models.Model]]:
        try:
            models_module = import_module('models')
            models_data = models_module.__dict__
            return [
                value for name, value in models_data.items()
                if self._is_valid_model(value) and not hasattr(models, name)
            ]
        except ImportError:
            return []

    def _load_default_builtin_models(self, custom_models: List[Type[models.Model]]) -> List[Type[models.Model]]:
        custom_table_types = {m.Meta.table_type for m in custom_models}
        return [
            getattr(models, name) for name in dir(models)
            if (
                    self._is_valid_model(getattr(models, name)) and
                    getattr(models, name).Meta.table_type not in custom_table_types
            )
        ]

    async def _add_async_queryset(self):
        for model in self.models:
            await model.apply_async()
        return self.models
