from enum import Enum

__all__ = [
    'TaskStatus',
    'SpiderType',
    'ScheduleType',
    'PriorityType',
    'DevelopmentStatus',
    'RunFrequency',
]


class TaskStatus(Enum):
    """任务状态"""
    before = '未开始'
    running = '进行中'
    success = '成功'
    error = '异常'
    canceled = '已取消'
    paused = '已暂停'


class SpiderType(Enum):
    """爬虫类型"""
    single = '单次'
    batch = '批次'
    increment = '增量'
    full = '全量'


class ScheduleType(Enum):
    """调度类型"""
    immediate = '立即执行'
    timing = '定时执行'
    cycle = '周期执行'
    trigger = '触发执行'


class PriorityType(Enum):
    """任务优先级"""
    low = '低'
    normal = '一般'
    high = '高'
    urgent = '紧急'


class DevelopmentStatus(Enum):
    """开发状态"""
    developing = '开发中'
    testing = '测试中'
    online = '已上线'
    maintaining = '维护中'
    abandoned = '已废弃'


class RunFrequency(Enum):
    """运行频率"""
    second = '秒级'
    minute = '分级'
    hour = '时级'
    day = '日级'
    week = '周级'
    month = '月级'
    season = '季级'
    year = '年级'
