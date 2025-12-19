import datetime
import functools
import random
import re
import time
from typing import List, Optional, Callable, Union

from AioSpider import logger
from AioSpider.exceptions import ScheduleError, ScheduleValueError, IntervalError


class CancelJob:
    """用于取消作业的标记类"""
    pass


class Scheduler:
    """
    调度器类,用于创建和管理作业
    """

    def __init__(self):
        self.jobs: List[Job] = []

    def run_pending(self):
        """
        运行所有应该运行的作业
        """
        runnable_jobs = sorted(job for job in self.jobs if job.should_run)
        for job in runnable_jobs:
            self._run_job(job)

    def run_all(self, delay_seconds: int = 0):
        """
        运行所有作业,不考虑是否应该运行
        
        :param delay_seconds: 作业之间的延迟时间(秒)
        """
        logger.level1(f"运行所有 {len(self.jobs)} 个作业,间隔 {delay_seconds} 秒")
        for job in self.jobs[:]:
            self._run_job(job)
            time.sleep(delay_seconds)

    def get_jobs(self) -> List["Job"]:
        """
        获取所有作业
        :return: 作业列表
        """
        return self.jobs[:]

    def clear(self):
        """
        删除所有作业
        """
        logger.level1("删除所有作业")
        self.jobs.clear()

    def cancel_job(self, job: "Job"):
        """
        取消指定的作业
        
        :param job: 要取消的作业
        """
        try:
            self.jobs.remove(job)
            logger.level1(f'取消作业 "{job}"')
        except ValueError:
            logger.level1(f'取消未调度的作业 "{job}"')

    def every(self, interval: int = 1) -> "Job":
        """
        创建一个新的周期性作业
        
        :param interval: 时间间隔
        :return: 新创建的作业
        """
        return Job(interval, self)

    def _run_job(self, job: "Job"):
        """
        运行作业并重新调度
        
        :param job: 要运行的作业
        """
        ret = job.run()
        if isinstance(ret, CancelJob) or ret is CancelJob:
            self.cancel_job(job)

    @property
    def next_run(self) -> Optional[datetime.datetime]:
        """
        获取下一次作业运行的时间
        
        :return: 下一次运行时间,如果没有作业则返回None
        """
        if not self.jobs:
            return None
        return min(self.jobs, key=lambda job: job.next_run).next_run

    @property
    def idle_seconds(self) -> Optional[float]:
        """
        获取距离下一次作业运行的空闲秒数
        
        :return: 空闲秒数,如果没有作业则返回None
        """
        if not self.next_run:
            return None
        return (self.next_run - datetime.datetime.now()).total_seconds()


class Job:
    """
    表示一个周期性作业
    """

    def __init__(self, interval: int, scheduler: Optional[Scheduler] = None):
        self.interval: int = interval
        self.latest: Optional[int] = None
        self.job_func: Optional[functools.partial] = None
        self.unit: Optional[str] = None
        self.at_time: Optional[datetime.time] = None
        self.at_time_zone = None
        self.last_run: Optional[datetime.datetime] = None
        self.next_run: Optional[datetime.datetime] = None
        self.start_day: Optional[str] = None
        self.cancel_after: Optional[datetime.datetime] = None
        self.scheduler: Optional[Scheduler] = scheduler

    def __lt__(self, other) -> bool:
        return self.next_run < other.next_run

    def __str__(self) -> str:
        job_func_name = getattr(self.job_func, "__name__", repr(self.job_func)) if self.job_func else "[None]"
        return f"Job(interval={self.interval}, unit={self.unit}, do={job_func_name}, args={self.job_func.args if self.job_func else '()'}, kwargs={self.job_func.keywords if self.job_func else '{}'}"

    def __repr__(self):
        return self._format_repr()

    def _format_repr(self):
        def format_time(t):
            return t.strftime("%Y-%m-%d %H:%M:%S") if t else "[never]"

        timestats = f"(last run: {format_time(self.last_run)}, next run: {format_time(self.next_run)})"

        if self.at_time is not None:
            return f"Every {self.interval} {self.unit[:-1] if self.interval == 1 else self.unit} at {self.at_time} do {self._format_call()} {timestats}"
        else:
            return f"Every {self.interval}{f' to {self.latest}' if self.latest is not None else ''} {self.unit[:-1] if self.interval == 1 else self.unit} do {self._format_call()} {timestats}"

    def _format_call(self):
        if self.job_func is None:
            return "[None]"
        args = [repr(x) if not isinstance(x, Job) else str(x) for x in self.job_func.args]
        kwargs = [f"{k}={repr(v)}" for k, v in self.job_func.keywords.items()]
        call_repr = f"{self.job_func.func.__name__}({', '.join(args + kwargs)})"
        return call_repr

    @property
    def seconds(self):
        self.unit = "seconds"
        return self

    @property
    def minutes(self):
        self.unit = "minutes"
        return self

    @property
    def hours(self):
        self.unit = "hours"
        return self

    @property
    def day(self):
        if self.interval != 1:
            raise IntervalError("使用 days 而不是 day")
        return self.days

    @property
    def days(self):
        self.unit = "days"
        return self

    @property
    def weeks(self):
        self.unit = "weeks"
        return self

    @property
    def month(self):
        self.unit = "months"
        return self
    
    @property
    def year(self):
        self.unit = "years"
        return self

    def _set_weekday(self, day: str) -> "Job":
        if self.interval != 1:
            raise IntervalError(f"每周{day}只允许用于每周作业。不支持每2周或更长时间的{day}作业。")
        self.start_day = day
        return self.weeks

    monday = property(lambda self: self._set_weekday("monday"))
    tuesday = property(lambda self: self._set_weekday("tuesday"))
    wednesday = property(lambda self: self._set_weekday("wednesday"))
    thursday = property(lambda self: self._set_weekday("thursday"))
    friday = property(lambda self: self._set_weekday("friday"))
    saturday = property(lambda self: self._set_weekday("saturday"))
    sunday = property(lambda self: self._set_weekday("sunday"))

    def at(self, time_str: str, tz: Optional[str] = None) -> "Job":
        """
        指定作业运行的具体时间
        
        :param time_str: 时间字符串
        :param tz: 时区
        :return: 作业实例
        """
        if self.unit not in ("days", "hours", "minutes") and not self.start_day:
            raise ScheduleValueError("无效的单位(有效单位为 `days`, `hours`, 和 `minutes`)")

        self._set_timezone(tz)
        self._parse_at_time(time_str)
        return self

    def _set_timezone(self, tz):
        if tz is not None:
            import pytz
            if isinstance(tz, str):
                self.at_time_zone = pytz.timezone(tz)
            elif isinstance(tz, pytz.BaseTzInfo):
                self.at_time_zone = tz
            else:
                raise ScheduleValueError("时区必须是字符串或 pytz.timezone 对象")

    def _parse_at_time(self, time_str: str):
        if not isinstance(time_str, str):
            raise TypeError("at() 应该传入一个字符串")

        if self.unit == "days" or self.start_day:
            if not re.match(r"^[0-2]\d:[0-5]\d(:[0-5]\d)?$", time_str):
                raise ScheduleValueError("每日作业的无效时间格式 (有效格式为 HH:MM(:SS)?)")
        elif self.unit == "hours":
            if not re.match(r"^([0-5]\d)?:[0-5]\d$", time_str):
                raise ScheduleValueError("每小时作业的无效时间格式 (有效格式为 (MM)?:SS)")
        elif self.unit == "minutes":
            if not re.match(r"^:[0-5]\d$", time_str):
                raise ScheduleValueError("每分钟作业的无效时间格式 (有效格式为 :SS)")

        time_values = time_str.split(":")
        if len(time_values) == 3:
            hour, minute, second = time_values
        elif len(time_values) == 2 and self.unit == "minutes":
            hour, minute, second = 0, 0, time_values[1]
        elif len(time_values) == 2 and self.unit == "hours" and time_values[0]:
            hour, minute, second = 0, *time_values
        else:
            hour, minute, second = *time_values, 0

        hour = int(hour)
        minute = int(minute)
        second = int(second)

        if self.unit == "days" or self.start_day:
            if not 0 <= hour <= 23:
                raise ScheduleValueError(f"无效的小时数 ({hour} 不在 0 到 23 之间)")

        self.at_time = datetime.time(hour, minute, second)

    def until(self, until_time: Union[datetime.datetime, datetime.timedelta, datetime.time, str]) -> "Job":
        """
        设置作业运行的截止时间
        
        :param until_time: 截止时间
        :return: 作业实例
        """
        self.cancel_after = self._parse_until_time(until_time)
        if self.cancel_after < datetime.datetime.now():
            raise ScheduleValueError("不能将作业调度到过去的时间")
        return self

    def _parse_until_time(self, until_time):
        if isinstance(until_time, datetime.datetime):
            return until_time
        elif isinstance(until_time, datetime.timedelta):
            return datetime.datetime.now() + until_time
        elif isinstance(until_time, datetime.time):
            return datetime.datetime.combine(datetime.datetime.now(), until_time)
        elif isinstance(until_time, str):
            return self._parse_datetime_str(until_time)
        else:
            raise TypeError("until() 接受 string, datetime.datetime, datetime.timedelta, datetime.time 参数")

    def _parse_datetime_str(self, datetime_str: str) -> datetime.datetime:
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%H:%M:%S", "%H:%M"]
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(datetime_str, fmt)
                if "-" not in datetime_str:
                    now = datetime.datetime.now()
                    dt = dt.replace(year=now.year, month=now.month, day=now.day)
                return dt
            except ValueError:
                pass
        raise ScheduleValueError("无效的字符串格式")

    def do(self, job_func: Callable, *args, **kwargs) -> "Job":
        """
        指定每次作业运行时应该调用的函数
        
        :param job_func: 要调用的函数
        :param args: 传递给函数的位置参数
        :param kwargs: 传递给函数的关键字参数
        :return: 作业实例
        """
        self.job_func = functools.partial(job_func, *args, **kwargs)
        functools.update_wrapper(self.job_func, job_func)
        self._schedule_next_run()
        if self.scheduler is None:
            raise ScheduleError("无法将作业添加到调度器。作业未与调度器关联")
        self.scheduler.jobs.append(self)
        return self

    @property
    def should_run(self) -> bool:
        """
        检查作业是否应该运行
        
        :return: 如果作业应该运行则返回True
        """
        return self.next_run is not None and datetime.datetime.now() >= self.next_run

    def run(self):
        """
        运行作业并立即重新调度
        
        :return: 作业函数的返回值,如果作业已过期则返回CancelJob
        """
        now = datetime.datetime.now()
        if self._is_overdue(now):
            logger.level1(f"取消作业 {self}")
            return CancelJob

        logger.level1(f"运行作业 {self}")
        ret = self.job_func()
        self.last_run = now
        self._schedule_next_run()

        if self._is_overdue(self.next_run):
            logger.level1(f"取消作业 {self}")
            return CancelJob
        return ret

    def _schedule_next_run(self):
        """
        计算作业下一次运行的时间
        """
        if self.unit not in ("seconds", "minutes", "hours", "days", "weeks"):
            raise ScheduleValueError("无效的单位 (有效单位为 `seconds`, `minutes`, `hours`, `days`, 和 `weeks`)")

        if self.latest is not None:
            if not (self.latest >= self.interval):
                raise ScheduleError("`latest` 大于 `interval`")
            interval = random.randint(self.interval, self.latest)
        else:
            interval = self.interval

        now = datetime.datetime.now(self.at_time_zone)
        next_run = now

        if self.start_day is not None:
            if self.unit != "weeks":
                raise ScheduleValueError("`unit` 应该是 'weeks'")
            next_run = self._move_to_weekday(next_run, self.start_day)

        if self.at_time is not None:
            next_run = self._move_to_at_time(next_run)

        period = datetime.timedelta(**{self.unit: interval})
        if interval != 1:
            next_run += period

        while next_run <= now:
            next_run += period

        next_run = self._correct_utc_offset(next_run, fixate_time=(self.at_time is not None))

        if self.at_time_zone is not None:
            next_run = next_run.astimezone().replace(tzinfo=None)

        self.next_run = next_run

    def _move_to_at_time(self, moment: datetime.datetime) -> datetime.datetime:
        """
        将给定的时间移动到作业的at_time
        """
        if self.at_time is None:
            return moment

        kwargs = {"second": self.at_time.second, "microsecond": 0}

        if self.unit == "days" or self.start_day is not None:
            kwargs["hour"] = self.at_time.hour

        if self.unit in ["days", "hours"] or self.start_day is not None:
            kwargs["minute"] = self.at_time.minute

        moment = moment.replace(**kwargs)
        moment = self._correct_utc_offset(moment, fixate_time=True)

        return moment

    def _correct_utc_offset(self, moment: datetime.datetime, fixate_time: bool) -> datetime.datetime:
        """
        修正UTC偏移
        """
        if self.at_time_zone is None:
            return moment

        offset_before = moment.utcoffset()
        moment = self.at_time_zone.normalize(moment)
        offset_after = moment.utcoffset()

        if offset_before == offset_after:
            return moment

        if not fixate_time:
            return moment

        offset_diff = offset_after - offset_before
        moment -= offset_diff

        re_normalized_offset = self.at_time_zone.normalize(moment).utcoffset()
        if re_normalized_offset != offset_after:
            moment += offset_diff

        return moment

    def _is_overdue(self, when: datetime.datetime) -> bool:
        """
        检查作业是否已过期
        """
        return self.cancel_after is not None and when > self.cancel_after

    @staticmethod
    def _move_to_weekday(moment: datetime.datetime, weekday: str) -> datetime.datetime:
        """
        将给定的时间移动到最近的指定工作日
        """
        weekday_index = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(weekday)
        days_ahead = weekday_index - moment.weekday()
        if days_ahead < 0:
            days_ahead += 7
        return moment + datetime.timedelta(days=days_ahead)
