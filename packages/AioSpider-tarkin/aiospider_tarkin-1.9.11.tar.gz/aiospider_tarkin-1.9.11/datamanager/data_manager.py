import asyncio
from copy import deepcopy
from collections import defaultdict
from typing import List, Type

from AioSpider import logger
from AioSpider.objects import DatabaseEngine, DatabaseCharset, TableType
from AioSpider.orm import Model
from AioSpider.tools import calculate_md5

# Crawlab SDK 是可选的，仅在部署到 Crawlab 平台时需要
try:
    from crawlab import save_item
    CRAWLAB_AVAILABLE = True
except ImportError:
    CRAWLAB_AVAILABLE = False
    save_item = None

from .filter import DataFilter


class DataManager:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.initialize()

    def __init__(self, settings, spider, models: List[Type[Model]]):
        self.settings = settings
        self.models = models
        self.spider = spider
        self.task_limit = settings.DataFilterConfig.TASK_LIMIT
        self.data_filter = self._create_data_filter()
        self.commit_count = 0
        self._items = defaultdict(list)
        self.stats = defaultdict(lambda: defaultdict(int))
        self.tasks = []

    def _create_data_filter(self) -> DataFilter:
        config = self.settings.DataFilterConfig
        return DataFilter(
            enabled=config.ENABLED,
            method=config.FILTER_METHOD,
            capacity=config.BLOOM_INIT_CAPACITY,
            max_capacity=config.BLOOM_MAX_CAPACITY,
            error_rate=config.BLOOM_ERROR_RATE,
        )

    async def initialize(self):
        """初始化数据管理器，创建表并加载数据"""
        self._create_tables()
        if self._should_load_data():
            await self._load_data()
        return self

    def _create_tables(self):
        from AioSpider.objects import DataBaseType
        for model in self.models:
            # 跳过 file 和 csv 类型，它们不需要创建表
            if model.Meta.database_type in [DataBaseType.file, DataBaseType.csv]:
                continue
            model.objects.create_table()
            model.objects.migrate()
        self._create_table_record()

    def get_table_model(self):
        return [i for i in self.models if i.Meta.table_type == TableType.table][0]

    def _create_table_record(self):
        from AioSpider.objects import DataBaseType
        table_model = self.get_table_model()
        for model in self.models:
            # 跳过 file 和 csv 类型的模型，它们不需要在表记录表中记录
            if model.Meta.database_type in [DataBaseType.file, DataBaseType.csv]:
                continue

            table_model.objects.create_or_update(
                table_name=model.table_name,
                model=model.__name__,
                schema_name=model.database,
                source=self.spider.source,
                spider_name=self.spider.name if model.Meta.table_type == TableType.data else 'AioSpider 框架',
                mark=model.__doc__,
                database_type=model.Meta.database_type,
                table_type=model.Meta.table_type,
                engine=DatabaseEngine(model.Meta.data_meta.engine),
                charset=DatabaseCharset(model.Meta.data_meta.charset)
            )

    def _update_table_record(self):
        from AioSpider.objects import DataBaseType
        table_model = self.get_table_model()
        for model in self.models:
            # 跳过 file 和 csv 类型的模型
            if model.Meta.database_type in [DataBaseType.file, DataBaseType.csv]:
                continue

            table_model.filter(
                table_name=model.table_name,
                schema_name=model.database
            ).update(
                spider_name=self.spider.name,
                total_count=model.get_total_rows(),
                data_length=model.get_data_length(),
                index_length=model.get_index_length(),
                last_update=model.get_last_update()
            )

    def _should_load_data(self) -> bool:
        config = self.settings.DataFilterConfig
        return config.ENABLED and config.LoadDataFromDB

    async def _load_data(self):
        for model in self.models:
            table = model.table_name
            unique_fields = model.get_unique_field()
            query = model.async_objects.only(*unique_fields) if unique_fields else model.async_objects
            data = await query.all()
            self.data_filter.add_items(table, [self._hash_item(item) for item in data])
            logger.level3(msg=f'从 {table} 表加载了 {len(data)} 条记录')

    @staticmethod
    def _hash_item(item: dict) -> str:
        return calculate_md5('-'.join(map(str, item.values())))

    async def close(self):
        await self._commit_all()
        self._update_table_record()
        self._log_stats()

    async def commit(self, model: Type[Model]):
        """提交数据到指定容器"""
        self.commit_count += 1
        table = model.table_name
        item = model.make_item()

        # 如果 Crawlab SDK 可用，保存数据到 Crawlab
        if CRAWLAB_AVAILABLE:
            save_item({})

        item_hash = self._generate_item_hash(item, model)

        if self.data_filter.contains(table, item_hash):
            logger.level4(msg=f"重复数据：{item}")
            return None

        self._items[table].append(model)
        if len(self._items[table]) >= model.Meta.commit_size:
            await self._commit_table(table)

    def _generate_item_hash(self, item: dict, model: Type[Model]) -> str:
        unique_fields = model.__class__.get_unique_field()
        if unique_fields:
            return calculate_md5('-'.join(self._hash_unique_fields(item, uf) for uf in unique_fields))
        return calculate_md5('-'.join(str(item.get(f.column)) for f in model.fields.values() if f.is_saved))

    @staticmethod
    def _hash_unique_fields(item: dict, unique_field: tuple) -> str:
        return '-'.join(str(item.get(f, "")) for f in unique_field)

    async def _commit_table(self, table: str):
        models = self._items[table]
        self.stats[table]['total'] += len(models)
        self.tasks.append(
            asyncio.create_task(self._save(table, deepcopy(models)))
        )
        self._items[table].clear()

        if len(self.tasks) >= self.task_limit:
            await asyncio.gather(*self.tasks)
            self.tasks.clear()

    async def _save(self, table: str, models: list):
        if not models:
            return
        model_class = models[0].__class__
        affect_count = await model_class.async_objects.bulk_create_or_update(models)
        self.stats[table]['affected'] += affect_count or 0
        logger.level3(
            msg=f'已提交 {len(models)} 条记录到 {table} 表，受影响 {affect_count} 条。'
                f'总计: {self.stats[table]["total"]}, 受影响: {self.stats[table]["affected"]}'
        )

    async def _commit_all(self):
        for table in list(self._items.keys()):
            await self._commit_table(table)

        if self.tasks:
            await asyncio.gather(*self.tasks)
            self.tasks.clear()

    def _log_stats(self):
        if any(self.stats.values()):
            tables = '、'.join(self.stats.keys())
            table_count = '、'.join([f"{self.stats[t]['total']:,}" for t in self.stats.keys()])
            table_affected = '、'.join([f"{self.stats[t]['affected']:,}" for t in self.stats.keys()])
            total = sum(s['total'] for s in self.stats.values())
            affected = sum(s['affected'] for s in self.stats.values())
            success_rate = affected / total * 100 if total > 0 else 0

            log_message = (
                    "数据保存统计\n" + "=" * 50 + " 爬虫关闭: 数据保存统计 " + "=" * 50 + "\n"
                                                                                          f"\t\t涉及表格:     {tables}\n"
                                                                                          f"\t\t表格记录数:   {table_count} 条\n"
                                                                                          f"\t\t表受影响数:   {table_affected} 条\n"
                                                                                          f"\t\t总记录数:     {total:,} 条\n"
                                                                                          f"\t\t总受影响数:   {affected:,} 条\n"
                                                                                          f"\t\t受影响率:     {success_rate:.2f}%\n"
                    + "=" * 120
            )
            logger.level3(msg=log_message)

    def get_total_count(self):
        return sum(s['total'] for s in self.stats.values())

    def get_total_effected_count(self):
        return sum(s['affected'] for s in self.stats.values())
