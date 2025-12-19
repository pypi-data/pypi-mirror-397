import copy
import json
import math
from typing import Union, Any, Iterable, Callable, List
from functools import wraps

import pydash
import numpy as np

from .time_tools import (
    strtime_to_stamp, stamp_to_strtime, strtime_to_time, stamp_to_time, time_to_stamp,
    get_relative_date, get_date_range, make_timestamp, get_quarter_end_dates
)
from .string_tools import re_text, join, re, re_match, re_sub, eval_string
from .encrypt_tools import aes_ecb_decrypt, make_md5, make_uuid, make_hmac, make_sha1, make_sha256
from .html_tools import xpath, xpath_text


def str2num(
        string: str, multi: Union[int, float] = 1, force: bool = False, _type: Callable = int,
        callable: Callable = None
) -> Union[int, float, str]:
    """
    数值转化
    Args:
        string: 待转化字符串
        multi: 倍乘系数
        force: 是否强制转化，指定为True时，若无法转化则返回0
        _type: 转换类型
    Return:
        转换后的数字类型，int | float | str
    """

    if string is None or not isinstance(string, (int, float, str)):
        if callable is None:
            return (_type() * multi) if force else string
        else:
            return callable((_type() * multi) if force else string)

    if isinstance(string, (int, float)):
        if callable is None:
            return _type(string * multi)
        else:
            return callable(_type(string * multi))

    string = re(string, r'([\d十百千万亿\.,%十百千万亿-]+)')

    if not string:
        if callable is None:
            return (_type() * multi) if force else string
        else:
            return callable((_type() * multi) if force else string)

    string = string[0].replace(',', '')
    has_percent = '%' in string
    neg = '-' in string

    units = {'十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}

    num = re(string, r'([\d\.]+)')
    if not num:
        if callable is None:
            return (_type() * multi) if force else string
        else:
            return callable((_type() * multi) if force else string)

    num = num[0]

    if num.isdigit():
        num = int(num)
    elif '.' in num and num.split('.')[0].isdigit() and num.split('.')[-1].isdigit():
        num = float(num)
    elif '.' in num and num[0] == '.' and num[1:].isdigit():
        num = float(num)
    else:
        if callable is None:
            return (_type() * multi) if force else string
        else:
            return callable((_type() * multi) if force else string)

    for unit, multiplier in units.items():
        if unit in string:
            num *= multiplier

    num = num / 100 if has_percent else num
    num = -num if neg else num
    num = num * multi
    
    if callable is None:
        return _type(num) if force else num
    else:
        return callable(_type(num) if force else num)


# -------------------- 数值处理 -------------------- #

def max(arry: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最大值
    Args:
        arry: 数组，如果传入可迭代对象，会强转成数组
        default: 默认值
    Return:
        序列的最大值
    """

    if not isinstance(arry, Iterable):
        return default

    try:
        arry = list(arry)
    except TypeError:
        return default

    if not arry:
        return default

    return np.max(arry)


def min(arry: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最小值
    Args:
        arry: 数组，如果传入可迭代对象，会强转成数组
        default: 默认值
    Return:
        序列的最小值
    """

    if not isinstance(arry, Iterable):
        return default

    try:
        arry = list(arry)
    except:
        return default

    if not arry:
        return default

    return np.min(arry)


def round_up(item: Union[float, int, str]) -> Union[int, float]:
    """
    向上取整
    Args:
        item: 待取整数据
    Return:
        取整数据后的数据
    """

    if isinstance(item, str):
        item = type_converter(item, to=float, force=True)

    return math.ceil(item)

# -------------------- 数值处理 -------------------- #


# ------------------ 爬虫常用工具 ------------------ #

def parse_json(
        json_data: dict, index: Union[str, Callable], default: Any = None,
        callback: Union[Callable, List[Callable]] = None
) -> Any:
    """
    字典取值
    Args:
        json_data: 原始数据
        index: 取值索引
        default: 默认值
    Return:
        从 json_data 中取到的值
    """
    if not isinstance(json_data, dict):
        return default

    data = pydash.get(json_data, index(json_data) if callable(index) else index, default)

    if callback is None:
        return data

    if isinstance(callback, Callable):
        return callback(data)

    if isinstance(callback, list):
        for clk in callback:
            data = clk(data)

    return data


def load_json(string: str, default: Any = None) -> Union[dict, list]:
    """
    将 json 字符串转化为字典
    Args:
        string: json 字符串
        default: 默认值
    Return:
        提取出的字典
    """

    if not string:
        return default or {}

    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return default or {}


def dump_json(data: Union[dict, list], separators: tuple = None, *args, **kwargs) -> str:
    """
    将字典转化为 json 字符串
    Args:
        data: 原始数据
        separators: 分隔符，为了获得最紧凑的JSON表示，指定为 （'，'，'：'） 以消除空白。
                    如果指定，应指定为（item_separator，key_separator）元组
    Return:
        json 字符串
    """
    return json.dumps(data, separators=separators, *args, **kwargs)


def type_converter(data: Any, to: Callable = None, force: bool = False) -> Any:
    """
    类型转换
    Args:
        data: 待转数据
        to: 转换类型
        force: 是否强制转换
    Return:
        转换值
    """

    def is_valid_number(data):
        if isinstance(data, str) and (
            data.isdigit() or ('.' in data and data.split('.')[0].isdigit() and data.split('.')[1].isdigit())
        ):
            return True
        return False

    if to is None or type(data) == to:
        return data

    if to in (int, float):
        if not isinstance(data, (int, float, str)) or (isinstance(data, str) and not is_valid_number(data)):
            return data if not force else to()

    return to(data)


# ------------------ 爬虫常用工具 ------------------ #


def deepcopy(item: Any) -> Any:
    """
    深拷贝
    Args:
        item: 待拷贝数据
    Return:
        深拷贝数据
    """

    return copy.deepcopy(item)


def convert_bool(value: Union[str, int, float, bool], default: bool = False):

    if value is None:
        return False

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        if (not value) or '否' in value or '-' in value or 'false' in value or 'N' in value or '不' in value or '暂停' in value:
            return False
        else:
            return True

    return default


def singleton(cls):

    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
