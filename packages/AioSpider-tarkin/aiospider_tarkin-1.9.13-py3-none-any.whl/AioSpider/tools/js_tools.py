import re
from pathlib import Path
from typing import Union

import execjs


def execute_js(path: Union[str, Path], func: str, encoding: str = 'utf-8'):
    """
    执行 js 文件
    Args:
        path: js 文件路径
        func: 需要调用的js方法
        encoding: 文件编码
    Return:
        执行结果 Any
    """

    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        return None

    if not path.is_file():
        return None

    ctx = execjs.compile(path.read_text(encoding=encoding))
    return ctx.call(func)


def filter_type(string: str) -> str:
    """
    将 js 中的 null、false、true、对象和数组过滤并转换成 python 对应的数据类型
    Args:
        string: 代转字符串
    Return:
        过滤后新的字符串
    """

    if 'null' in string:
        string = string.replace('null', 'None')

    if 'false' in string:
        string = string.replace('false', 'False')

    if 'true' in string:
        string = string.replace('true', 'True')

    # 将 JavaScript 对象转换为 Python 字典
    string = re.sub(r'\{(.+?)\}', r'dict(\1)', string)

    # 将 JavaScript 数组转换为 Python 列表
    string = re.sub(r'\[(.+?)\]', r'list(\1)', string)

    return string

