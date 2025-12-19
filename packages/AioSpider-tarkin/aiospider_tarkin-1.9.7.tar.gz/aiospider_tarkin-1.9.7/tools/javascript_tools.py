import re
from pathlib import Path
from typing import Union, Any, Dict

import execjs

__all__ = [
    'execute_js_file',
    'convert_js_to_python',
    'parse_js_object',
    'minify_js',
    'extract_js_functions',
    'js_to_python_function',
    'execute_js_code',
    'load_js_module',
]


def execute_js_file(file_path: Union[str, Path], function_name: str, *args, encoding: str = 'utf-8') -> Any:
    """
    执行 JavaScript 文件中的指定函数
    
    Args:
        file_path: JavaScript 文件路径
        function_name: 需要调用的 JavaScript 函数名
        *args: 传递给 JavaScript 函数的参数
        encoding: 文件编码
    
    Returns:
        执行结果
    
    Raises:
        FileNotFoundError: 如果文件不存在
        ValueError: 如果指定路径不是文件
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    
    if not path.is_file():
        raise ValueError(f"指定路径不是文件: {path}")
    
    js_code = path.read_text(encoding=encoding)
    ctx = execjs.compile(js_code)
    return ctx.call(function_name, *args)


def convert_js_to_python(js_string: str) -> str:
    """
    将 JavaScript 中的特殊值和数据结构转换为 Python 对应的类型
    
    Args:
        js_string: JavaScript 代码字符串
    
    Returns:
        转换后的 Python 代码字符串
    """
    conversions = {
        'null': 'None',
        'undefined': 'None',
        'false': 'False',
        'true': 'True'
    }
    
    for js_value, py_value in conversions.items():
        js_string = re.sub(r'\b{}\b'.format(js_value), py_value, js_string)
    
    # 将 JavaScript 对象转换为 Python 字典
    js_string = re.sub(r'\{(.+?)\}', lambda m: 'dict({})'.format(m.group(1)), js_string)
    
    # 将 JavaScript 数组转换为 Python 列表
    js_string = re.sub(r'\[(.+?)\]', lambda m: 'list({})'.format(m.group(1)), js_string)
    
    return js_string


def parse_js_object(js_object_string: str) -> Dict:
    """
    解析 JavaScript 对象字符串为 Python 字典
    
    Args:
        js_object_string: JavaScript 对象字符串
    
    Returns:
        解析后的 Python 字典
    """
    py_dict_string = convert_js_to_python(js_object_string)
    return eval(py_dict_string)


def minify_js(js_code: str) -> str:
    """
    压缩 JavaScript 代码
    
    Args:
        js_code: JavaScript 代码字符串
    
    Returns:
        压缩后的 JavaScript 代码
    """
    # 移除注释
    js_code = re.sub(r'//.*?\n|/\*.*?\*/', '', js_code, flags=re.DOTALL)
    
    # 移除多余的空白字符
    js_code = re.sub(r'\s+', ' ', js_code)
    
    # 移除行尾分号
    js_code = re.sub(r';\s*([}\)])', r'\1', js_code)
    
    return js_code.strip()


def extract_js_functions(js_code: str) -> Dict[str, str]:
    """
    提取 JavaScript 代码中的函数定义
    
    Args:
        js_code: JavaScript 代码字符串
    
    Returns:
        函数名和函数体的字典
    """
    function_pattern = re.compile(r'function\s+(\w+)\s*\((.*?)\)\s*\{(.*?)\}', re.DOTALL)
    return {name: body.strip() for name, params, body in function_pattern.findall(js_code)}


def js_to_python_function(js_function: str) -> callable:
    """
    将 JavaScript 函数转换为可调用的 Python 函数
    
    Args:
        js_function: JavaScript 函数代码字符串
    
    Returns:
        可调用的 Python 函数
    """
    return eval_js(js_function)


def execute_js_code(js_code: str, function_name: str, *args) -> Any:
    """
    执行 JavaScript 代码字符串中的指定函数
    
    Args:
        js_code: JavaScript 代码字符串
        function_name: 需要调用的 JavaScript 函数名
        *args: 传递给 JavaScript 函数的参数
    
    Returns:
        执行结果
    """
    ctx = execjs.compile(js_code)
    return ctx.call(function_name, *args)


def load_js_module(module_name: str) -> Any:
    """
    加载 Node.js 模块
    
    Args:
        module_name: 模块名称
    
    Returns:
        加载的模块对象
    
    Raises:
        ImportError: 如果模块加载失败
    """
    try:
        return execjs.require(module_name)
    except execjs.RuntimeError as e:
        raise ImportError(f"无法加载模块 {module_name}: {str(e)}")

