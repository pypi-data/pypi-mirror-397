from pydash import attempt

from AioSpider.objects import (
    TaskStatus,
    SpiderType,
    ScheduleType,
    PriorityType,
    EnvType,
    DevelopmentStatus,
    RunFrequency,
    TableType,
    DataBaseType,
    DatabaseEngine,
    DatabaseCharset,
)
from AioSpider.orm.fields import (
    CharField,
    DateTimeField,
    IntField,
    UUIDField,
    TinyIntField,
    EnumField,
    BooleanField,
    DateField,
    DecimalField,
    PathField
)
from .models import ABCModel

__all__ = [
    'TableModel',
    'TableStatisticsModel',
    'TableFieldStatisticsModel',
    'SpiderModel',
    'TaskModel',
    'TaskProgressModel'
]


class TableModel(ABCModel):
    """表数据结构"""

    table_name = CharField(name='表名', max_length=30, index=True)
    schema_name = CharField(name='库名', max_length=20, index=True)
    model = CharField(name='模型名称', max_length=30, index=True)
    spider_name = CharField(name='爬虫名称', max_length=20, index=True)
    mark = CharField(name='表备注', max_length=255, null=True)
    database_type = EnumField(name='数据库类型', choices=DataBaseType, default=DataBaseType.sqlite)
    table_type = EnumField(name='表类型', choices=TableType, default=TableType.data)
    engine = EnumField(name='数据库引擎', max_length=20, choices=DatabaseEngine)
    charset = EnumField(name='字符集', max_length=20, choices=DatabaseCharset)
    total_count = IntField(name='数据总条数', default=0)
    data_length = IntField(name='数据长度', default=0)
    index_length = IntField(name='索引长度', default=0)
    is_active = BooleanField(name='是否激活', default=True)
    last_update = DateTimeField(name='最后更新时间', null=True)

    order = [
        'id', 'table_name', 'schema_name', 'model', 'spider_name', 'mark', 'database_type', 'table_type', 'engine',
        'charset', 'total_count', 'data_length', 'index_length', 'is_active', 'last_update',
        'source', 'create_time', 'update_time'
    ]

    class Meta:
        table_type = TableType.table
        composite_unique_indexes = (
            ('table_name', 'schema_name'),
        )


class TableStatisticsModel(ABCModel):
    """表数据统计数据结构"""

    task_id = CharField(name='任务ID', max_length=36, min_length=36, index=True)
    date = DateField(name='统计日期', index=True)
    table_name = CharField(name='表名', max_length=30, index=True)
    schema_name = CharField(name='库名', max_length=20, index=True)
    add_count = IntField(name='新增数据量', default=0)
    update_count = IntField(name='更新数据量', default=0)
    total_count = IntField(name='总数据量', default=0)

    class Meta:
        table_type = TableType.statistics
        composite_unique_indexes = (
            ('task_id', 'date', 'table_name', 'schema_name'),
        )

    order = [
        'id', 'task_id', 'date', 'table_name', 'schema_name', 'add_count', 'update_count', 'total_count',
        'source', 'create_time', 'update_time'
    ]


class TableFieldStatisticsModel(ABCModel):
    """表字段数据统计数据结构"""

    task_id = CharField(name='任务ID', max_length=36, min_length=36, index=True)
    date = DateField(name='统计日期', index=True)
    table_name = CharField(name='表名', max_length=30, index=True)
    schema_name = CharField(name='库名', max_length=20, index=True)
    field_name = CharField(name='字段名', max_length=30, index=True)
    field_type = CharField(name='字段类型', max_length=20)
    null_count = IntField(name='空值数量', null=True)
    unique_count = IntField(name='唯一值数量', null=True)
    zero_count = IntField(name='零值数量', null=True)
    max_value = DecimalField(name='最大值', max_length=20, null=True, allow_int=True)
    min_value = DecimalField(name='最小值', max_length=20, null=True, allow_int=True)
    avg_value = DecimalField(name='平均值', max_length=20, null=True, allow_int=True)
    sum_value = DecimalField(name='总和', max_length=25, null=True, allow_int=True)
    std_value = DecimalField(name='标准差', max_length=20, null=True, allow_int=True)
    variance_value = DecimalField(name='方差', max_length=25, null=True, allow_int=True)
    null_rate = DecimalField(name='空值比例', null=True, allow_int=True)
    unique_rate = DecimalField(name='唯一值比例', null=True, allow_int=True)
    max_length = IntField(name='最大长度', null=True)
    min_length = IntField(name='最小长度', null=True)
    avg_length = DecimalField(name='平均长度', max_length=20, null=True, allow_int=True)

    class Meta:
        table_type = TableType.statistics
        composite_unique_indexes = (
            ('task_id', 'date', 'table_name', 'schema_name', 'field_name'),
        )

    order = [
        'id', 'task_id', 'date', 'table_name', 'schema_name', 'field_name', 'field_type', 'null_count', 'unique_count',
        'zero_count', 'max_value', 'min_value', 'avg_value', 'sum_value', 'std_value', 'variance_value',
        'null_rate', 'unique_rate', 'max_length', 'min_length', 'avg_length', 'source', 'create_time', 'update_time'
    ]


class SpiderModel(ABCModel):
    """爬虫数据结构"""

    name = CharField(name='爬虫名称', max_length=20, unique=True)
    spider_type = EnumField(name='爬虫类型', default=SpiderType.single, choices=SpiderType, index=True)
    site = CharField(name='站点名称', max_length=20, null=True, index=True)
    host = CharField(name='主机', max_length=120)
    root = PathField(name='根目录', max_length=200)
    target = CharField(name='目标页面', max_length=255, null=True)
    description = CharField(name='描述', max_length=600, null=True)
    develop_status = EnumField(name='开发状态', default=DevelopmentStatus.developing, choices=DevelopmentStatus)
    frequency = EnumField(name='运行频率', default=RunFrequency.day, choices=RunFrequency)
    version = CharField(name='版本号', max_length=120, default='1.0')
    author = CharField(name='作者', max_length=50, null=True)
    maintainer = CharField(name='维护者', max_length=50, null=True)
    email = CharField(name='联系邮箱', max_length=100, null=True)
    priority = EnumField(name='优先级', default=PriorityType.normal, choices=PriorityType)
    is_active = BooleanField(name='是否激活', default=True)
    tags = CharField(name='标签', max_length=255, null=True)

    order = [
        'id', 'name', 'spider_type', 'site', 'host', 'root', 'target', 'description', 'development_status', 'frequency', 'version',
        'author', 'maintainer', 'email', 'priority', 'is_active', 'tags', 'source', 'create_time', 'update_time'
    ]

    class Meta:
        table_type = TableType.spider


class TaskModel(ABCModel):
    """批次爬虫任务数据结构"""

    task_id = UUIDField(name='任务ID', unique=True)
    task_name = CharField(name='任务名称', max_length=50)
    spider = CharField(name='爬虫名称', max_length=30, index=True)
    crawl_start = DateTimeField(name='开始采集时间', null=True, allow_timestamp=True)
    crawl_end = DateTimeField(name='结束采集时间', null=True, allow_timestamp=True)
    status = EnumField(name='任务状态', default=TaskStatus.before, choices=TaskStatus)
    retry_count = TinyIntField(name='重试次数', default=0, unsigned=True)
    schedule_type = EnumField(name='调度类型', default=ScheduleType.immediate, choices=ScheduleType)
    priority = EnumField(name='任务优先级', default=PriorityType.normal, choices=PriorityType)

    crawl_count = IntField(name='采集数据条数', default=0, unsigned=True)
    save_count = IntField(name='保存数据条数', default=0, unsigned=True)
    success_request_count = IntField(name='成功请求数量', default=0, unsigned=True)
    failure_request_count = IntField(name='失败请求数量', default=0, unsigned=True)

    env = EnumField(name='环境', default=EnvType.debug, choices=EnvType)

    order = [
        'id', 'task_id', 'task_name', 'spider', 'crawl_start', 'crawl_end', 'status', 'crawl_count', 'save_count',
        'success_request_count', 'failure_request_count', 'schedule_type', 'priority', 'env',
        'source', 'create_time', 'update_time'
    ]

    class Meta:
        table_type = TableType.task

    def clean(self, item):
        item['task_name'] = f"{item['spider']}_{self.task_id}"
        return item


class TaskProgressModel(ABCModel):
    """批次爬虫任务进度数据结构"""

    task_id = CharField(name='任务ID', max_length=36, min_length=36, index=True)
    datetime = DateTimeField(name='时间', index=True)
    progress = DecimalField(name='进度', default=0.0, allow_int=True, unsigned=True)
    running_time = DecimalField(name='程序运行时间', null=True, allow_int=True, unsigned=True)
    completed_count = IntField(name='已完成请求数量', default=0, unsigned=True)
    success_count = IntField(name='成功请求数量', default=0, unsigned=True)
    failure_count = IntField(name='失败请求数量', default=0, unsigned=True)
    waiting_count = IntField(name='等待请求数量', default=0, unsigned=True)
    avg_speed = DecimalField(name='当前并发速度', null=True, allow_int=True, unsigned=True)
    remaining_time = DecimalField(name='预计剩余时间', null=True, allow_int=True, unsigned=True)
    crawl_count = IntField(name='采集数据条数', default=0, unsigned=True)
    save_count = IntField(name='保存数据条数', default=0, unsigned=True)

    order = [
        'id', 'task_id', 'datetime', 'progress', 'running_time', 'completed_count', 'success_count', 'failure_count',
        'waiting_count', 'avg_speed', 'remaining_time', 'crawl_count', 'save_count', 'source', 'create_time', 'update_time'
    ]

    class Meta:
        table_type = TableType.task_progress
        composite_unique_indexes = (
            ('task_id', 'datetime'),
        )
