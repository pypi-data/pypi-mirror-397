from enum import IntEnum
from datetime import datetime, timedelta, time as dtime, date
from typing import Union, Callable, NewType, Optional

from AioSpider import tools
from AioSpider.exceptions import SpiderExeption, StatusTags
from AioSpider.tools.time_tools import get_next_month_same_day

from .spider import Spider


token = NewType('token', str)


class BatchLevel(IntEnum):

    SECOND = 0
    MINUTE = 1
    HOUR = 2
    DAY = 3
    WEEK = 4
    MONTH = 5
    SEASON = 6
    YEAR = 7


class BatchSpider(Spider):
    """
    批次爬虫，支持秒级、分钟级、小时级、天级、月级、年级批次定时
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        level: 爬虫批次级别
            1: 秒级
            2: 分钟级
            3: 小时级
            4: 天级
            5: 周级
            6: 月级
            7: 季级
            8: 年级批次定时
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    INTERVAL_LEVEL = {
        BatchLevel.SECOND: ('seconds', 1),
        BatchLevel.MINUTE: ('minutes', 1),
        BatchLevel.HOUR: ('hours', 1),
        BatchLevel.DAY: ('days', 1),
        BatchLevel.WEEK: ('days', 7),
    }

    def __init__(
            self,
            *,
            time: Union[datetime, str],
            interval: int,
            level: BatchLevel,
            users: str = None,
            cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None,
            call_end: Callable[[], bool] = None,
            call_login: Callable[[str, str], str] = None,
    ):

        super(BatchSpider, self).__init__(
            users=users, cookies=cookies, token=token, call_before=call_before, call_end=call_end, 
            call_login=call_login
        )
        if isinstance(time, str):
            time = tools.strtime_to_time(time, is_time=True)

        self.level = level
        self.interval = interval
        self.time = time
        self.next_time = self._init_next_time()

    def start(self):
        from AioSpider.core import BatchEngine
        BatchEngine(self).start()

    def get_next_time(self):
        return self.next_time + timedelta(**{
            self.INTERVAL_LEVEL[self.level][0]: self.INTERVAL_LEVEL[self.level][-1] * self.interval
        })

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            hour=self.time.hour, minute=self.time.minute,
            second=self.time.second, microsecond=0
        )

        if next_time < now:
            next_time += timedelta(**{
                self.INTERVAL_LEVEL[self.level][0]: self.INTERVAL_LEVEL[self.level][-1] * self.interval
            })

        return next_time


class BatchSecondSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 1, users: str = None, cookies: dict = None,
            token: str = None, call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable = None,
    ):
        super().__init__(
            time=time, interval=interval, level=BatchLevel.SECOND, users=users, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )


class BatchMiniteSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 2, users: str = None, cookies: dict = None, 
            token: str = None, call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable= None,
    ):
        super().__init__(
            time=time, interval=interval, level=BatchLevel.MINUTE, users=users, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )


class BatchHourSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 1, users: str = None, 
            cookies: dict = None, token: str = None, call_before: Callable[[], bool] = None,
            call_end: Callable[[], bool] = None, call_login: Callable = None,
    ):
        super().__init__(
            time=time, interval=interval, level=BatchLevel.HOUR, users=users, 
            cookies=cookies, token=token, call_before=call_before, call_end=call_end, call_login=call_login
        )


class BatchDaySpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户名
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 1, users: str = None, cookies: dict = None, 
            token: str = None, call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable = None,
    ):
        super(BatchDaySpider, self).__init__(
            time=time, interval=interval, level=BatchLevel.DAY, users=users, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )


class BatchWeekSpider(BatchSpider):
    """
    日级爬虫
    Args:
        weekdays: 周几，1-7，周一~周日（天、七），星期一~星期日（天、七）
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    mapping = {
        '周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5, '周六': 6, '周日': 7, '周天': 7, '周七': 7,
        '星期一': 1, '星期二': 2, '星期三': 3, '星期四': 4, '星期五': 5, '星期六': 6, '星期日': 7, '星期天': 7, '星期七': 7,
    }

    def __init__(
            self, *, weekdays: Union[int, list, tuple, str], time: Union[dtime, str], interval: int = 1,
            users: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable = None,
    ):
        
        if isinstance(weekdays, (int, str)):
            weekdays = [weekdays]

        weekdays = [self.mapping.get(i, i) for i in weekdays]

        if not set(weekdays) & set(range(1, 8)):
            raise SpiderExeption(status=StatusTags.InvalidParams, msg='weekends')
            
        self.weekdays = weekdays
        super().__init__(
            time=time, interval=interval, users=users, level=BatchLevel.WEEK, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()
        next_time = now.replace(
            hour=self.time.hour, minute=self.time.minute,
            second=self.time.second, microsecond=0
        )

        while True:
            if (next_time.weekday() + 1) in self.weekdays and next_time > now:
                break
            tmp_date = tools.before_day(now=next_time, before=-1, is_date=True)
            next_time = next_time.replace(
                year=tmp_date.year, month=tmp_date.month, day=tmp_date.day
            )

        return next_time

    def get_next_time(self):

        next_time = self.next_time
        while True:
            tmp_date = tools.before_day(now=next_time, before=-1, is_date=True)
            next_time = next_time.replace(
                year=tmp_date.year, month=tmp_date.month, day=tmp_date.day
            )
            if (next_time.weekday() + 1) in self.weekdays:
                return next_time


class BatchMonthSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, days: Union[int, list, str], time: Union[dtime, str], interval: int = 1,
            users: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable = None,
    ):

        if isinstance(days, (int, str)):
            days = [days]

        if not set(days) & set(range(1, 32)):
            raise SpiderExeption(status=StatusTags.InvalidParams, msg='days')

        self.days = days

        super().__init__(
            time=time, interval=interval, level=BatchLevel.MONTH, users=users, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            hour=self.time.hour, minute=self.time.minute,
            second=self.time.second, microsecond=0
        )

        while True:
            if next_time.day in self.days and next_time > now:
                break
            tmp_date = tools.before_day(now=next_time, before=-1, is_date=True)
            next_time = next_time.replace(
                year=tmp_date.year, month=tmp_date.month, day=tmp_date.day
            )

        return next_time

    def get_next_time(self):

        next_time = self.next_time
        while True:
            tmp_date = tools.before_day(now=next_time, before=-1, is_date=True)
            next_time = next_time.replace(
                year=tmp_date.year, month=tmp_date.month, day=tmp_date.day
            )
            if next_time.day in self.days:
                return next_time


class BatchSeasonSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, date: Union[date, str], time: Union[dtime, str], interval: int = 1, users: str = None, 
            cookies: dict = None, token: str = None, call_before: Callable[[], bool] = None, 
            call_end: Callable[[], bool] = None, call_login: Callable = None
    ):

        if isinstance(date, str):
            date = tools.strtime_to_time(date, is_date=True)

        self.date = date

        super().__init__(
            time=time, interval=interval, users=users, level=BatchLevel.SEASON, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            year=self.date.year, month=self.date.month, day=self.date.day,
            hour=self.time.hour, minute=self.time.minute, second=self.time.second,
            microsecond=0
        )

        if next_time < now:
            for _ in range(3):
                next_time = get_next_month_same_day(next_time)

        return next_time

    def get_next_time(self):
        next_time = self.next_time
        for _ in range(3):
            next_time = get_next_month_same_day(next_time)
        return next_time


class BatchYearSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        users: 登录用户
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, date: Union[date], time: Union[dtime, str], interval: int = BatchLevel.YEAR, users: str = None, 
            cookies: dict = None, token: str = None, call_before: Callable[[], bool] = None, 
            call_end: Callable[[], bool] = None, call_login: Callable = None
    ):

        if isinstance(date, str):
            date = tools.strtime_to_time(date, is_date=True)

        self.date = date

        super().__init__(
            time=time, interval=interval, users=users, level=BatchLevel.YEAR, cookies=cookies, token=token, 
            call_before=call_before, call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            year=self.date.year, month=self.date.month, day=self.date.day,
            hour=self.time.hour, minute=self.time.minute, second=self.time.second,
            microsecond=0
        )

        if next_time < now:
            next_time = now.replace(
                year=self.date.year + 1, month=self.date.month, day=self.date.day,
                hour=self.time.hour, minute=self.time.minute, second=self.time.second,
                microsecond=0
            )

        return next_time

    def get_next_time(self):
        return self.next_time.replace(
            year=self.next_time.year + 1, month=self.next_time.month, day=self.next_time.day,
            hour=self.next_time.hour, minute=self.next_time.minute, second=self.next_time.second,
            microsecond=0
        )
