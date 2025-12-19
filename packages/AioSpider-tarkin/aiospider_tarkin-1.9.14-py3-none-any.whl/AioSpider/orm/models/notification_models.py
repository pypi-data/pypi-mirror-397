from AioSpider.objects import NoticeType, TableType
from AioSpider.orm.fields import CharField, TextField, DateTimeField, EnumField

from .models import ABCModel

__all__ = ['NoticeModel']


class NoticeModel(ABCModel):

    spider_name = CharField(name='爬虫名称', max_length=20)
    task_id = CharField(name='任务ID', max_length=36, min_length=36)
    notice_time = DateTimeField(name='预警时间', allow_string=True)
    level = CharField(name='等级', max_length=6, min_length=6)
    type = EnumField(name='类型', max_length=20, choices=NoticeType, default=NoticeType.warning)
    message = TextField(name='消息')
    env = CharField(name='环境', max_length=20)
    server_ip = CharField(name='服务器IP', max_length=20)
    exception_stack = TextField(name='异常堆栈')
    impact_range = CharField(name='影响范围', max_length=20, null=True)
    suggestion = CharField(name='建议操作', max_length=20, null=True)
    performance_info = CharField(name='性能指标', max_length=50)


    order = [
        'spider_name', 'task_id', 'level', 'type', 'message', 'env', 'server_ip', 'exception_stack', 'impact_range',
        'suggestion', 'performance_info'
    ]

    class Meta:
        table_type = TableType.notice
        composite_unique_indexes = (
            ('spider_name', 'task_id', 'notice_time'),
        )
