import time as time_module
from datetime import datetime, time
from typing import Union, Callable, List, Generator

from AioSpider import logger
from AioSpider.objects import SpiderType, DevelopmentStatus, RunFrequency, PriorityType, ScheduleType
from AioSpider.http import Response, HttpRequest
from AioSpider.middleware.user_pool import BaseUser

from .schedule import Scheduler

__all__ = ['Spider']


class Spider:
    """
        爬虫类
        Args:
            at: 调度时间
                立即执行：为None
                定时执行：为时间字符串或时间元组
                周期执行：为时间字符串或时间元组和天数
                触发执行：为条件函数
            interval: 周期执行的间隔时间，单位为秒
            users: 用户列表
            call_before: 爬虫启动前执行的函数
            call_end: 爬虫结束时执行的函数
    """

    name: str = None
    spider_type: SpiderType = SpiderType.single
    schedule_type: ScheduleType = ScheduleType.immediate
    frequency: RunFrequency = RunFrequency.day
    source: str = None
    description: str = None
    target: str = None
    develop_status: DevelopmentStatus = DevelopmentStatus.developing
    version: str = '1.0'
    author: str = None
    maintainer: str = None
    email: str = None
    priority: PriorityType = PriorityType.normal
    is_active: bool = True
    tags: Union[str, List[str]] = None

    start_req_list: List[HttpRequest] = []

    class SpiderRequestConfig:
        pass

    class ConcurrencyStrategyConfig:
        pass

    class ConnectPoolConfig:
        pass

    class DataFilterConfig:
        pass

    class RequestFilterConfig:
        pass

    class RequestProxyConfig:
        pass

    class BrowserConfig:
        pass

    def __init__(
            self,
            *,
            at: Union[str, tuple, list, Callable[[], bool]] = None,
            interval: int = 1,
            users: Union[BaseUser, List[BaseUser]] = None,
            call_before: Callable[[], bool] = None,
            call_end: Callable[[], bool] = None,
            **kwargs
    ):
        self.at = self._parse_at(at)
        self.interval = interval
        self.users: list = users
        self.cust_call_before: Callable[[], bool] = call_before or (lambda: True)
        self.cust_call_end: Callable[[], bool] = call_end or (lambda: True)
        self._engine = None
        self.scheduler = Scheduler()

        # 允许通过kwargs覆盖类属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.set_name()

    def _parse_at(self, at):
        if isinstance(at, str):
            return at
        elif callable(at):
            return at
        elif isinstance(at, (tuple, list)):
            if len(at) == 2:
                time_str, days = at
                if isinstance(days, str):
                    return (time_str, days)
                elif isinstance(days, (tuple, list)):
                    return (time_str, list(days))
            elif len(at) > 2:
                return list(at)
        return at

    def run(self):
        schedule_map = {
            ScheduleType.immediate: self.start,
            ScheduleType.cycle: self.start_cycle,
            ScheduleType.timing: self.start_timing,
            ScheduleType.trigger: self.start_trigger
        }
        
        run_method = schedule_map.get(self.schedule_type)
        if run_method:
            run_method()
        else:
            raise ValueError(f'不支持的调度类型：{self.schedule_type}')

    def start(self):
        """立即执行"""
        from AioSpider.core import Engine
        self._engine = Engine(self)
        self._engine.start() 
        
    def start_cycle(self):
        """周期执行"""
        default_at = {
            RunFrequency.second: None,
            RunFrequency.minute: time().strftime(":%S"),
            RunFrequency.hour: time().strftime("%M:%S"),
            RunFrequency.day: time().strftime("%H:%M:%S"),
            RunFrequency.week: (time().strftime("%H:%M:%S"), 'monday'),
            RunFrequency.month: time().strftime("%H:%M:%S"),
        }
        frequency_map = {
            RunFrequency.second: self.scheduler.every(self.interval).seconds,
            RunFrequency.minute: self.scheduler.every(self.interval).minutes,
            RunFrequency.hour: self.scheduler.every(self.interval).hours,
            RunFrequency.day: self.scheduler.every(self.interval).days,
            RunFrequency.week: self.scheduler.every(self.interval).weeks,
        }

        job_func = frequency_map.get(self.frequency)
        if not job_func:
            raise ValueError(f'不支持的运行频率：{self.frequency}')

        at_value = self.at if self.at else default_at[self.frequency]
        
        if self.frequency == RunFrequency.week:
            at_time, weekday = at_value
            job = getattr(weekday, job_func).at(at_time)
        elif self.frequency == RunFrequency.second:
            job = job_func
        else:
            job = job_func.at(at_value)

        job.do(self.start)

        while True:
            self.scheduler.run_pending()
            print(datetime.now())
            time_module.sleep(1)

    def start_timing(self):
        """定时执行"""
        if isinstance(self.at, tuple):
            time_str, days = self.at
            if isinstance(days, str):
                if days == 'weekday':
                    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                        self.scheduler.every().day.at(time_str).do(self.start)
                elif days == 'weekend':
                    self.scheduler.every().saturday.at(time_str).do(self.start)
                    self.scheduler.every().sunday.at(time_str).do(self.start)
                else:
                    getattr(self.scheduler.every(), days).at(time_str).do(self.start)
            elif isinstance(days, list):
                for day in days:
                    getattr(self.scheduler.every(), day).at(time_str).do(self.start)
        elif isinstance(self.at, list):
            for time_str in self.at:
                self.scheduler.every().day.at(time_str).do(self.start)
        else:
            self.scheduler.every().day.at(self.at).do(self.start)

        while True:
            self.scheduler.run_pending()
            time_module.sleep(1)

    def start_trigger(self):
        """触发执行"""
        while self.at():
            self.start()

    def set_name(self):
        if self.name is None:
            self.name = self.__class__.__name__

    def spider_open(self):
        logger.level3(msg=f'------------------- 爬虫：{self.name} 已启动 -------------------')

    def spider_close(self):
        logger.level3(msg=f'------------------- 爬虫：{self.name} 已关闭 -------------------')

    def start_requests(self) -> Generator[HttpRequest, None, None]:
        yield from self.start_req_list

    def parse(self, response):
        """
            解析回调函数
            @params: response: Response对象
            @return: Request | dict | None
        """
        pass

    def login(self, username: str, password: str) -> str:
        return ''

    def process_200(self, request: HttpRequest, response: Response):
        """
        处理响应状态码为200的请求
        Args:
            request: 请求对象
            response: 响应对象
        Return
            None | Request | Response | False
            返回None则表示不做任何处理
            返回Request则表示重新发起请求
            返回Response则表示直接返回响应
            返回False则表示丢弃该请求
        """
        return None
    
    def process_404(self, request: HttpRequest, response: Response):
        return None
    
    def process_407(self, request: HttpRequest, response: Response):
        return None
