import re
from typing import Any, Iterable, Union, List
from pprint import pformat
import unicodedata
import difflib
import string
import random

__all__ = [
    'join_strings', 
    'contains_chinese', 
    'extract_with_regex', 
    'matches_regex', 
    'extract_first_match',
    'replace_with_regex',
    'safe_eval',
    'pretty_format',
    'normalize_unicode',
    'levenshtein_distance',
    'generate_random_string',
    'find_longest_common_substring',
    'camel_to_snake_case',
    'snake_to_camel_case',
    'split_camel_case',
    'join_words',
    'remove_non_alphanumeric',
    'is_palindrome',
    'reverse_string',
    'count_words'
]


def join_strings(data: Iterable, separator: str = '') -> str:
    """
    拼接字符串
    Args:
        data: 可迭代对象，若data中的元素有非字符串类型的，会被强转
        separator: 连接符
    Return:
        拼接后的字符串
    """
    return separator.join(map(str, data))


def contains_chinese(text: str) -> bool:
    """判断字符串是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def extract_with_regex(text: str, pattern: str, default: Any = None, flags: int = re.S) -> list:
    """
    使用正则表达式提取数据
    Args:
        text: 原始文本数据
        pattern: 正则表达式
        default: 默认值
        flags: 正则表达式标志
    Return:
        匹配结果列表或默认值
    """
    result = re.findall(pattern, text, flags)
    return result if result else default if default is not None else []


def matches_regex(text: str, pattern: str) -> bool:
    """
    正则匹配
    Args:
        text: 原始文本数据
        pattern: 正则表达式
    Return: 
        bool
    """
    return bool(re.match(pattern, text))


def extract_first_match(text: str, pattern: str, default: Any = '', flags: int = re.S) -> Union[str, Any]:
    """
    正则提取第一个匹配的文本数据
    Args:
        text: 原始文本数据
        pattern: 正则表达式
        default: 默认值
        flags: 正则表达式标志
    Return:
        第一个匹配结果或默认值
    """
    result = extract_with_regex(text, pattern, default, flags)
    return result[0] if result else default


def replace_with_regex(text: str, pattern: str, replacement: str) -> str:
    """
    使用正则表达式替换文本
    Args:
        text: 原始文本数据
        pattern: 正则表达式
        replacement: 替换值
    Return:
        替换后的字符串
    """
    return re.sub(pattern, replacement, text)


def safe_eval(expression: str, default: Any = None) -> Any:
    """
    安全执行字符串表达式
    Args:
        expression: 字符串表达式
        default: 默认值
    Return:
        表达式执行结果或默认值
    """
    try:
        return eval(expression)
    except Exception:
        return default


def pretty_format(obj: Any, indent: int = 1, width: int = 80, depth: int = None, *, compact: bool = False, sort_dicts: bool = True, underscore_numbers: bool = False) -> str:
    """
    格式化对象为易读字符串
    Args:
        obj: 要格式化的对象
        indent: 缩进空格数
        width: 每行最大宽度
        depth: 最大递归深度
        compact: 是否使用紧凑格式
        sort_dicts: 是否对字典排序
        underscore_numbers: 是否使用下划线分隔数字
    Return:
        格式化后的字符串
    """
    return pformat(
        obj, indent=indent, width=width, depth=depth, compact=compact, 
        sort_dicts=sort_dicts, underscore_numbers=underscore_numbers
    )


def normalize_unicode(text: str, form: str = 'NFKC') -> str:
    """
    Unicode 标准化
    Args:
        text: 输入文本
        form: 标准化形式 ('NFC', 'NFKC', 'NFD', 'NFKD')
    Return:
        标准化后的文本
    """
    return unicodedata.normalize(form, text)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    计算两个字符串的 Levenshtein 距离
    Args:
        s1: 第一个字符串
        s2: 第二个字符串
    Return:
        Levenshtein 距离
    """
    return sum(1 for x, y in zip(s1, s2) if x != y) + abs(len(s1) - len(s2))


def generate_random_string(length: int, charset: str = string.ascii_letters + string.digits) -> str:
    """
    生成指定长度的随机字符串
    Args:
        length: 字符串长度
        charset: 字符集
    Return:
        随机字符串
    """
    return ''.join(random.choice(charset) for _ in range(length))


def find_longest_common_substring(s1: str, s2: str) -> str:
    """
    查找两个字符串的最长公共子串
    Args:
        s1: 第一个字符串
        s2: 第二个字符串
    Return:
        最长公共子串
    """
    matcher = difflib.SequenceMatcher(None, s1, s2)
    match = matcher.find_longest_match(0, len(s1), 0, len(s2))
    return s1[match.a: match.a + match.size]


def camel_to_snake_case(string: str) -> str:
    """
    将驼峰命名转换为蛇形命名
    Args:
        string: 驼峰命名的字符串
    Return:
        蛇形命名的字符串
    """
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', string).lower()


def snake_to_camel_case(string: str) -> str:
    """
    将蛇形命名转换为驼峰命名
    Args:
        string: 蛇形命名的字符串
    Return:
        驼峰命名的字符串
    """
    return string.replace('_', '').title().replace('_', '')


def split_camel_case(string: str) -> List[str]:
    """
    将驼峰命名拆分为单词列表
    Args:
        string: 驼峰命名的字符串
    Return:
        单词列表
    """
    return [char for char in string if char.isupper()]


def join_words(words: Iterable[str], separator: str = '') -> str:
    """
    将单词列表连接为字符串
    Args:
        words: 单词列表
        separator: 连接符
    Return:
        连接后的字符串
    """
    return separator.join(words)


def remove_non_alphanumeric(string: str) -> str:
    """
    删除字符串中的非字母数字字符
    Args:
        string: 输入字符串
    Return:
        删除非字母数字字符后的字符串
    """
    return re.sub(r'[^a-zA-Z0-9]', '', string)


def is_palindrome(string: str) -> bool:
    """
    判断字符串是否为回文
    Args:
        string: 输入字符串
    Return:
        bool
    """
    return string == string[::-1]


def reverse_string(string: str) -> str:
    """
    反转字符串
    Args:
        string: 输入字符串
    Return:
        反转后的字符串
    """
    return string[::-1]


def count_words(string: str) -> int:
    """
    计算字符串中的单词数
    Args:
        string: 输入字符串
    Return:
        单词数
    """
    return len(re.findall(r'\b\w+\b', string))
