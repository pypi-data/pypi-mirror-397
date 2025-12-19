from AioSpider.exceptions import AioException

__all__ = [
    'ScheduleError',
    'ScheduleValueError',
    'IntervalError',
]


class ScheduleError(AioException):
    pass


class ScheduleValueError(ScheduleError):
    """调度值错误"""
    pass


class IntervalError(ScheduleValueError):
    """无效的时间间隔"""
    pass
