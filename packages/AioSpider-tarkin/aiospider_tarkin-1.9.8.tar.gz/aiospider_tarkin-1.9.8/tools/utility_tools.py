import copy
import json
import math
import re
import time
import os
from functools import wraps
from decimal import Decimal, InvalidOperation
from importlib.util import find_spec
from typing import Union, Any, Iterable, Callable, List, Dict, Optional
from AioSpider import logger
import pydash


__all__ = [
    'string_to_number',
    'find_max',
    'find_min',
    'ceil',
    'parse_json_data',
    'load_json_string',
    'dump_json_string',
    'convert_type',
    'deep_copy',
    'to_boolean',
    'singleton',
    'flatten_dict',
    'deep_update',
    'safe_divide',
    'get_package_path',
    'convert_bool'
]



def string_to_number(
        value: Union[str, int, float],
        multiplier: Union[int, float] = 1,
        force_convert: bool = False,
        target_type: Callable = int,
        callback: Optional[Callable] = None
) -> Union[int, float, str]:
    """
    将字符串或数值转换为指定类型的数值
    功能：
        1. 将字符串转换为数值
        2. 将数值转换为指定类型的数值
        3. 将数值乘以指定的乘数
        4. 可以转换含有中文的数值
            1万 -> 10000
            1亿 -> 100000000
            1.1万 -> 11000
            1.1亿 -> 110000000
        5. 可以转换含有 % 的数值
            1.1% -> 0.011
            1.12% -> 0.0112
    Args:
        value: 待转换的值
        multiplier: 乘数
        force_convert: 是否强制转换，若为True则无法转换时返回0
        target_type: 目标数值类型
        callback: 后处理函数
    Return:
        转换后的数值，int | float | str
    """
    def process_result(result):
        return callback(result) if callback else result

    if value is None or not isinstance(value, (int, float, str)):
        return process_result((target_type() * multiplier) if force_convert else value)

    if isinstance(value, (int, float)):
        return process_result(target_type(value * multiplier))

    value = re.search(r'([-+]?[\d十百千万亿\.,%]+)', str(value))
    if not value:
        return process_result((target_type() * multiplier) if force_convert else value)

    value = value.group(1).replace(',', '')
    has_percent = '%' in value

    units = {'十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
    for unit, unit_value in units.items():
        value = value.replace(unit, f'*{unit_value}')

    try:
        num = eval(value.rstrip('%'))
        num = Decimal(str(num))
    except (SyntaxError, InvalidOperation):
        return process_result((target_type() * multiplier) if force_convert else value)

    num = num / 100 if has_percent else num
    num *= Decimal(multiplier)

    try:
        result = target_type(num)
    except ValueError:
        result = float(num) if target_type == int else int(num)

    return process_result(result)



def find_max(sequence: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最大值
    Args:
        sequence: 可迭代对象
        default: 默认值
    Return:
        序列的最大值
    """
    try:
        return max(sequence)
    except (ValueError, TypeError):
        return default


def find_min(sequence: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最小值
    Args:
        sequence: 可迭代对象
        default: 默认值
    Return:
        序列的最小值
    """
    try:
        return min(sequence)
    except (ValueError, TypeError):
        return default


def ceil(value: Union[float, int, str]) -> int:
    """
    向上取整
    Args:
        value: 待取整数据
    Return:
        取整后的数据
    """
    if isinstance(value, str):
        value = float(value)
    return math.ceil(value)


def parse_json_data(
        json_data: Dict[str, Any], 
        key_path: Union[str, Callable], 
        default: Any = None,
        transformations: Union[Callable, List[Callable]] = None
) -> Any:
    """
    从JSON数据中提取并转换值
    Args:
        json_data: 原始JSON数据
        key_path: 取值路径或函数
        default: 默认值
        transformations: 转换函数或函数列表
    Return:
        从json_data中提取并转换的值
    """
    if not isinstance(json_data, dict):
        return default

    data = pydash.get(json_data, key_path(json_data) if callable(key_path) else key_path, default)

    # if data == default:
    #     logger.level5(msg=f'key_path: {key_path} not found in json_data')

    if transformations is None:
        return data

    if callable(transformations):
        return transformations(data)

    if isinstance(transformations, list):
        for transform in transformations:
            data = transform(data)

    return data


def load_json_string(json_string: str, default: Any = None) -> Union[Dict, List]:
    """
    将JSON字符串转换为Python对象
    Args:
        json_string: JSON字符串
        default: 默认值
    Return:
        转换后的Python对象
    """
    if not json_string:
        return default or {}

    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return default or {}


def dump_json_string(data: Union[Dict, List], separators: tuple = None, *args, **kwargs) -> str:
    """
    将Python对象转换为JSON字符串
    Args:
        data: 原始数据
        separators: 分隔符，为了获得最紧凑的JSON表示，指定为 （'，'，'：'） 以消除空白。
                    如果指定，应指定为（item_separator，key_separator）元组
    Return:
        JSON字符串
    """
    return json.dumps(data, separators=separators, *args, **kwargs)


def convert_type(data: Any, target_type: Callable = None, force: bool = False) -> Any:
    """
    类型转换
    Args:
        data: 待转换数据
        target_type: 目标类型
        force: 是否强制转换
    Return:
        转换后的值
    """
    def is_valid_number(value):
        return isinstance(value, str) and (value.isdigit() or (
            '.' in value and value.replace('.', '', 1).isdigit()
        ))

    if target_type is None or isinstance(data, target_type):
        return data

    if target_type in (int, float):
        if not isinstance(data, (int, float, str)) or (isinstance(data, str) and not is_valid_number(data)):
            return data if not force else target_type()

    try:
        return target_type(data)
    except (ValueError, TypeError):
        return data if not force else target_type()


def deep_copy(item: Any) -> Any:
    """
    深拷贝
    Args:
        item: 待拷贝数据
    Return:
        深拷贝后的数据
    """
    return copy.deepcopy(item)


def to_boolean(value: Union[str, int, float, bool], default: bool = False) -> bool:
    """
    将各种类型的值转换为布尔值
    Args:
        value: 待转换的值
        default: 默认值
    Return:
        转换后的布尔值
    """
    if value is None:
        return False

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        value = value.lower()
        if value in ('false', 'no', 'n', '0', 'off', 'disable', 'disabled'):
            return False
        elif value in ('true', 'yes', 'y', '1', 'on', 'enable', 'enabled'):
            return True
        
        if value:
            return True

    return default


def singleton(cls):
    """
    单例模式装饰器
    """
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

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

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    将嵌套字典扁平化
    Args:
        d: 待扁平化的字典
        parent_key: 父键
        sep: 键分隔符
    Return:
        扁平化后的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_update(d: Dict, u: Dict) -> Dict:
    """
    深度更新字典
    Args:
        d: 待更新的字典
        u: 用于更新的字典
    Return:
        更新后的字典
    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: Union[int, float] = 0) -> Union[int, float]:
    """
    安全除法，避免除数为零的错误
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值，当分母为零时返回
    Return:
        除法结果或默认值
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    重试装饰器
    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟时间
        backoff: 延迟时间的增长因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_attempts:
                        raise e
                    time.sleep(delay * (backoff ** (attempt - 1)))
        return wrapper
    return decorator


def memoize(func):
    """
    记忆化装饰器，缓存函数的计算结果
    """
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


def get_package_path(package_name: str) -> str:
    """
    获取指定包在当前虚拟环境中site-packages的具体路径。

    参数:
        package_name (str): 要查找的包名。

    返回:
        str: 包的绝对路径。

    异常:
        ImportError: 如果找不到指定的包。
    """
    spec = find_spec(package_name)
    if spec is None:
        raise ImportError(f"无法找到包 '{package_name}'。")
    
    if spec.submodule_search_locations:
        # 包可能包含子模块，返回第一个搜索路径
        package_path = os.path.abspath(next(iter(spec.submodule_search_locations)))
    else:
        # 包是单个模块文件，返回其所在目录
        package_path = os.path.dirname(os.path.abspath(spec.origin))
    
    return package_path
