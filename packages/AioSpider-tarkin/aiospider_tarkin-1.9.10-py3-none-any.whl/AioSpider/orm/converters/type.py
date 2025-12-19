import json
import re
import time
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Callable, Optional, Any, Type, Union, Tuple

from .base import BaseConverter

__all__ = [
    "type_converter",
    "str_to_bool",
    "str_to_datetime",
    "json_to_dict",
    "str_to_pattern",
    "non_to_list",
    "non_to_tuple",
    "str_to_list",
    "str_to_date",
    "str_to_enum",
    "datetime_to_date",
    "timestamp_to_date",
    "str_to_time",
    "datetime_to_time",
    "timestamp_to_time",
    "str_to_timestamp",
    "date_to_timestamp",
    "datetime_to_timestamp",
    "time_to_datetime",
    "timestamp_to_datetime",
    "str_to_datetime",
    "date_to_datetime",
    "str_to_float",
    "int_to_float",
    "float_to_int",
    "str_to_int",
    "decimal_to_float",
]


@dataclass(kw_only=True, slots=True, repr=True)
class TypeConverter(BaseConverter):

    from_type: Optional[Union[Type, Tuple[Type, ...]]] = field(default=None, repr=True)
    expected_type: Callable = field(default=None, repr=True)

    def func(self, value: Any, field_name: str) -> Any:
        if isinstance(value, self.from_type):
            return self.expected_type(value)
        return value


def type_converter(from_type: Optional[Union[Type, Tuple[Type, ...]]], expected_type: Callable) -> TypeConverter:
    return TypeConverter(from_type=from_type, expected_type=expected_type)


def str_to_bool() -> TypeConverter:
    """将字符串转换为布尔值。"""
    return type_converter(str, lambda v: v.lower() in ('true', 'yes', '1', 'on'))


def json_to_dict() -> TypeConverter:
    """将JSON字符串转换为字典。"""
    return type_converter(str, json.loads)


def str_to_pattern() -> TypeConverter:
    """将字符串转换为正则表达式。"""
    return type_converter(str, re.compile)


def non_to_list() -> TypeConverter:
    """将None转换为空列表。"""
    return type_converter(type(None), lambda v: [])


def non_to_tuple() -> TypeConverter:
    """将None转换为空元组。"""
    return type_converter(type(None), lambda v: ())


def str_to_list() -> TypeConverter:
    """将字符串转换为列表。"""
    return type_converter(str, lambda v: [v, ])


def str_to_enum(choices) -> TypeConverter:
    """将字符串转换为列表。"""
    return type_converter(str, lambda v: choices(v))


# --------------------------- 日期时间转换 --------------------------- #

def str_to_date(formats=None) -> TypeConverter:
    """将字符串转换为日期。"""
    if formats is None:
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"]

    def convert_to_date(value: str) -> date:
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"无法将字符串转换为日期: {value!r}")
    
    return type_converter(str, convert_to_date)


def datetime_to_date() -> TypeConverter:
    """将日期时间转换为日期。"""
    return type_converter(datetime, lambda v: v.date())


def timestamp_to_date() -> TypeConverter:
    """将时间戳转换为日期。"""
    return type_converter(int, lambda v: datetime.fromtimestamp(v).date() if len(str(v)) == 10 else datetime.fromtimestamp(v/1000).date())


def str_to_time(formats: str = "%H:%M:%S") -> TypeConverter:
    """将字符串转换为时间。"""
    return type_converter(str, lambda v: datetime.strptime(v, formats).time())


def datetime_to_time() -> TypeConverter:
    """将日期时间转换为时间。"""
    return type_converter(datetime, lambda v: v.time()) 


def timestamp_to_time() -> TypeConverter:
    """将时间戳转换为时间。"""
    return type_converter(int, lambda v: datetime.fromtimestamp(v).time() if len(str(v)) == 10 else datetime.fromtimestamp(v/1000).time())


def str_to_timestamp(formats: str = "%Y-%m-%d %H:%M:%S") -> TypeConverter:
    """将字符串转换为时间戳。"""
    return type_converter(str, lambda v: int(time.mktime(time.strptime(v, formats))))


def date_to_timestamp() -> TypeConverter:
    """将日期转换为时间戳。"""
    return type_converter(date, lambda v: int(time.mktime(v.timetuple())))


def datetime_to_timestamp() -> TypeConverter:
    """将日期时间转换为时间戳。"""
    return type_converter(datetime, lambda v: int(time.mktime(v.timetuple())))


def time_to_datetime() -> TypeConverter:
    """将时间转换为日期时间。"""
    return type_converter(time, lambda v: datetime.combine(date.today(), v))


def timestamp_to_datetime() -> TypeConverter:
    """将时间戳转换为日期时间。"""
    return type_converter((int, float), lambda v: datetime.fromtimestamp(v))


def str_to_datetime(formats: str = "%Y-%m-%d %H:%M:%S") -> TypeConverter:
    """将字符串转换为日期时间。"""
    return type_converter(str, lambda v: datetime.strptime(v, formats))


def date_to_datetime() -> TypeConverter:
    """将日期转换为日期时间。"""
    return type_converter(date, lambda v: datetime.combine(v, time()))

# --------------------------- 数字转换 --------------------------- #

def str_to_float() -> TypeConverter:
    """将字符串转换为浮点数。"""
    return type_converter(str, float)


def int_to_float() -> TypeConverter:
    """将整数转换为浮点数。"""
    return type_converter(int, float)


def decimal_to_float() -> TypeConverter:
    """将Decimal转换为浮点数。"""
    return type_converter(Decimal, float)


def float_to_int() -> TypeConverter:
    """将浮点数转换为整数。"""
    return type_converter(float, int)


def str_to_int() -> TypeConverter:
    """将字符串转换为整数。"""
    return type_converter(str, int)

