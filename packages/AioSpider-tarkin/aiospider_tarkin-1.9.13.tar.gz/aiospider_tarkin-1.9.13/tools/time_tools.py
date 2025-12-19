import calendar
import re
import time
from typing import Optional, Union, List, Callable
from datetime import datetime, date, timedelta, time as dtime
from zoneinfo import ZoneInfo


__all__ = [
    'strtime_to_stamp', 
    'stamp_to_strtime', 
    'strtime_to_time', 
    'stamp_to_time', 
    'time_to_stamp',
    'get_relative_date',
    'get_date_range', 
    'make_timestamp', 
    'get_quarter_end_dates', 
    'get_next_month_same_day',
    'get_business_days', 
    'get_fiscal_year_dates', 
    'parse_relative_time', 
    'get_time_difference', 
    'convert_timezone'
]


class TimeConverter:
    """
    高级时间转换器：时间字符串、时间戳、日期时间对象相互转换
    """

    DATE_FORMATS = [
        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
        "%Y%m%d %H:%M:%S.%f", "%Y%m%d %H:%M:%S", "%Y%m%d %H:%M", "%Y%m%d",
        '%H:%M:%S.%f', '%H:%M:%S'
    ]

    @classmethod
    def _find_matching_format(cls, time_str: str) -> Optional[str]:
        for fmt in cls.DATE_FORMATS:
            try:
                datetime.strptime(time_str, fmt)
                return fmt
            except ValueError:
                continue
        return None

    @classmethod
    def _to_datetime(cls, time_str: str, format: str = None) -> Optional[datetime]:
        if not time_str or not isinstance(time_str, str):
            return None

        time_str = time_str.strip()

        if format is not None:
            return datetime.strptime(time_str, format)

        time_str = re.sub('[年月/]', '-', time_str)
        time_str = re.sub('[日]', '', time_str)

        matching_format = cls._find_matching_format(time_str)
        return datetime.strptime(time_str, matching_format) if matching_format else None

    @classmethod
    def strtime_to_stamp(cls, time_str: str, format: str = None, millisecond: bool = False) -> Optional[int]:
        """
        时间字符串转时间戳
        """
        dt = cls._to_datetime(time_str, format)
        return int(dt.timestamp() * 1000) if dt and millisecond else int(dt.timestamp()) if dt else None

    @classmethod
    def stamp_to_strtime(cls, timestamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
        """
        时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
        """
        if timestamp is None or not isinstance(timestamp, (int, float, str)):
            return None

        if isinstance(timestamp, str) and timestamp.isdigit():
            timestamp = float(timestamp)

        if len(str(timestamp).split('.')[0]) <= len(str(int(time.time()))):
            return time.strftime(format, time.localtime(timestamp))
        elif len(str(timestamp).split('.')[0]) <= len(str(int(time.time() * 1000))):
            return time.strftime(format, time.localtime(timestamp / 1000))
        else:
            return None

    @classmethod
    def strtime_to_time(
            cls, time_str: str, format: str = None, as_date: bool = False, as_time: bool = False
    ) -> Union[datetime, date, dtime, None]:
        """
        时间字符串转日期时间类型
        """
        dt = cls._to_datetime(time_str, format)
        if not dt:
            return dt
        elif as_date:
            return dt.date()
        elif as_time:
            return dt.time()
        else:
            return dt

    @classmethod
    def stamp_to_time(
            cls, timestamp: Union[int, float, str], as_date: bool = False, timezone: str = 'Asia/Shanghai'
    ) -> Union[datetime, date, None]:
        """
        时间戳转时间对象，支持秒级（10位）和毫秒级（13位）时间戳自动判断
        """
        if timestamp is None or not isinstance(timestamp, (int, float, str)):
            return None

        if isinstance(timestamp, str):
            timestamp = float(timestamp)

        if len(str(timestamp).split('.')[0]) <= len(str(int(time.time()))):
            dt = datetime(1970, 1, 1, tzinfo=ZoneInfo('UTC')) + timedelta(seconds=timestamp)
        elif len(str(timestamp).split('.')[0]) <= len(str(int(time.time() * 1000))):
            dt = datetime(1970, 1, 1, tzinfo=ZoneInfo('UTC')) + timedelta(milliseconds=timestamp)
        else:
            return None

        dt = dt.astimezone(ZoneInfo(timezone))
        return dt.date() if as_date else dt

    @classmethod
    def time_to_stamp(cls, time_obj: Union[datetime, date], millisecond: bool = False) -> Optional[int]:
        """
        时间对象转时间戳
        """
        if not isinstance(time_obj, (datetime, date)):
            return None

        if isinstance(time_obj, date):
            time_obj = datetime(time_obj.year, time_obj.month, time_obj.day)

        return int(time_obj.timestamp() * 1000) if millisecond else int(time_obj.timestamp())


def strtime_to_stamp(time_str: str, format: str = None, millisecond: bool = False) -> Optional[int]:
    return TimeConverter.strtime_to_stamp(time_str, format=format, millisecond=millisecond)


def stamp_to_strtime(timestamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
    return TimeConverter.stamp_to_strtime(timestamp, format=format)


def strtime_to_time(
        time_str: str, format: str = None, as_date: bool = False, as_time: bool = False
) -> Union[datetime, date, dtime, None]:
    return TimeConverter.strtime_to_time(time_str, format=format, as_date=as_date, as_time=as_time)


def stamp_to_time(
        timestamp: Union[int, float, str], as_date: bool = False, timezone: str = 'Asia/Shanghai'
) -> Union[datetime, date, None]:
    return TimeConverter.stamp_to_time(timestamp, as_date=as_date, timezone=timezone)


def time_to_stamp(time_obj: Union[datetime, date], millisecond: bool = False) -> Optional[int]:
    return TimeConverter.time_to_stamp(time_obj, millisecond=millisecond)


def get_relative_date(
        reference_date: Optional[str] = None, days_before: int = 0, month_before: int = 0, year_before: int = 0,
        as_date: bool = False, as_str: bool = False, skip_weekend: bool = False
) -> Union[datetime, date, str]:
    """
    获取相对日期
    
    Args:
        reference_date: 参考日期，默认为当前时间
        days_before: 向前推移的天数
        month_before: 向前推移的月数
        year_before: 向前推移的年数
        as_date: 是否返回date类型
        as_str: 是否返回字符串类型
        skip_weekend: 是否跳过周末，默认为False
    """
    def skip_weekend_func(day: date):
        while day.weekday() in [5, 6]:
            day -= timedelta(days=1)
        return day

    if reference_date is None:
        reference_date = datetime.now()
    else:
        reference_date = datetime.strptime(reference_date, '%Y-%m-%d')
        # 先处理年和月的偏移
    year = reference_date.year - year_before
    month = reference_date.month - month_before
    
    # 处理月份向前借位
    while month <= 0:
        month += 12
        year -= 1

    # 获取目标月份的天数
    _, days_in_month = calendar.monthrange(year, month)
    
    # 确保日期有效
    day = min(reference_date.day, days_in_month)

    # 构建新的日期时间
    result_date = datetime(
        year=year,
        month=month,
        day=day,
        hour=reference_date.hour,
        minute=reference_date.minute,
        second=reference_date.second,
        microsecond=reference_date.microsecond
    )
    result_date = result_date - timedelta(days=days_before)
    if skip_weekend:
        result_date = skip_weekend_func(result_date)
    if as_date:
        result_date = result_date.date()

    if as_str:
        result_date = str(result_date)

    return result_date


def get_date_range(
        start: Union[int, str, date] = 0,
        end: Union[int, str, date] = 0,
        skip_weekend: bool = False,
        skip_func: Union[bool, Callable] = None,
        as_string: bool = False
) -> List[Union[date, str]]:
    """
    生成日期范围
    
    Args:
        start: 开始日期，可以是相对天数(int)、日期字符串或date对象，默认为今天
        end: 结束日期，可以是相对天数(int)、日期字符串或date对象，默认为今天
        skip_weekend: 是否跳过周末，默认为False
        skip_func: 过滤函数，True表示跳过周末，None表示不过滤，也可传入自定义过滤函数
        as_string: 是否返回字符串格式，默认为False
    Returns:
        List[Union[date, str]]: 日期列表
    """
    def skip_weekend_func(date_list):
        return [d for d in date_list if d.weekday() not in [5, 6]]

    if isinstance(start, str):
        start = strtime_to_time(start, as_date=True)
    elif isinstance(start, int):
        start = get_relative_date(days_before=start, as_date=True)
    elif not isinstance(start, date):
        raise TypeError("start参数类型错误,必须是int、str或date类型")
        
    if isinstance(end, str):
        end = strtime_to_time(end, as_date=True)
    elif isinstance(end, int):
        end = get_relative_date(days_before=end, as_date=True)
    elif not isinstance(end, date):
        raise TypeError("end参数类型错误,必须是int、str或date类型")
        
    if start > end:
        raise ValueError("开始日期不能大于结束日期")
        
    date_list = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    
    if skip_weekend:
        date_list = skip_weekend_func(date_list)
    
    if skip_func is not None:
        date_list = skip_func(date_list)
        
    return [d.strftime('%Y-%m-%d') if as_string else d for d in date_list]


def make_timestamp(millisecond: bool = True, as_string: bool = False) -> Union[int, str]:
    """
    获取当前时间戳
    """
    timestamp = int(time.time() * 1000) if millisecond else int(time.time())
    return str(timestamp) if as_string else timestamp


def get_quarter_end_dates(start_year: int, end_year: int, as_string: bool = True) -> List[str]:
    """
    获取指定年份范围内每个季度的最后一天
    
    Args:
        start_year: 起始年份
        end_year: 结束年份
        as_string: 是否返回字符串格式
    Returns:
        List[str]: 季度末日期列表,格式为YYYY-MM-DD
    """
    quarter_ends = []
    for year in range(start_year, end_year + 1):
        for month in (3, 6, 9, 12):
            quarter_end = date(year, month, calendar.monthrange(year, month)[1])
            quarter_ends.append(str(quarter_end) if as_string else quarter_end)
    return quarter_ends


def get_next_month_same_day(current_date: Union[str, datetime], as_date=False) -> Union[date, datetime]:
    """
    获取下个月的同一天
    """
    if isinstance(current_date, str):
        current_date = strtime_to_time(current_date)

    year, month = current_date.year, current_date.month
    day, time = current_date.day, current_date.time()

    if month == 12:
        next_month, year = 1, year + 1
    else:
        next_month = month + 1

    days_in_next_month = 31 if next_month in [1, 3, 5, 7, 8, 10, 12] else (
        30 if next_month != 2 else 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    )

    day = min(day, days_in_next_month)

    return date(year, next_month, day) if as_date else datetime(
        year, next_month, day, time.hour, time.minute, time.second
    )


def get_business_days(start_date: Union[str, date, datetime], end_date: Union[str, date, datetime]) -> int:
    """
    计算两个日期之间的工作日数量
    """
    def skip_weekend(date_list):
        return [d for d in date_list if d.weekday() not in [5, 6]]

    if isinstance(start_date, str):
        start_date = strtime_to_time(start_date, as_date=True)
    if isinstance(end_date, str):
        end_date = strtime_to_time(end_date, as_date=True)
    
    return len(get_date_range(start_date, end_date, skip_weekend=True))


def get_fiscal_year_dates(fiscal_year: int, start_month: int = 4) -> tuple:
    """
    获取指定财年的起始和结束日期
    """
    start_date = date(fiscal_year - 1, start_month, 1)
    end_date = date(fiscal_year, start_month, 1) - timedelta(days=1)
    return start_date, end_date


def parse_relative_time(time_str: str) -> datetime:
    """
    解析相对时间字符串，如"2天前"、"3小时后"等
    """
    now = datetime.now()
    match = re.match(r'(\d+)\s*(天|小时|分钟)(前|后)', time_str)
    if match:
        num, unit, direction = match.groups()
        num = int(num)
        if unit == '天':
            delta = timedelta(days=num)
        elif unit == '小时':
            delta = timedelta(hours=num)
        else:
            delta = timedelta(minutes=num)
        
        return now - delta if direction == '前' else now + delta
    else:
        raise ValueError("无法解析的时间字符串")


def get_time_difference(time1: Union[str, datetime], time2: Union[str, datetime], unit: str = 'seconds') -> float:
    """
    计算两个时间之间的差值
    """
    if isinstance(time1, str):
        time1 = strtime_to_time(time1)
    if isinstance(time2, str):
        time2 = strtime_to_time(time2)
    
    diff = abs(time1 - time2)
    
    if unit == 'seconds':
        return diff.total_seconds()
    elif unit == 'minutes':
        return diff.total_seconds() / 60
    elif unit == 'hours':
        return diff.total_seconds() / 3600
    elif unit == 'days':
        return diff.days
    else:
        raise ValueError("不支持的时间单位")


def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """
    转换时区
    """
    from_zone = ZoneInfo(from_tz)
    to_zone = ZoneInfo(to_tz)
    return dt.replace(tzinfo=from_zone).astimezone(to_zone)

