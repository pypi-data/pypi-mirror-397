from pathlib import Path
from typing import List, Dict, Optional, Union


def read_template(template_name: str) -> str:
    """读取模板文件内容"""
    path = Path(__file__).parent / f'{template_name}.tpl'
    return path.read_text(encoding='utf-8')


def is_path(path: str) -> bool:
    """
    判断是否是路径
    
    Args:
        path: 待判断的字符串
    
    Returns:
        bool: 是否为路径
    """
    return any(char in path for char in ('\\', '/', '~'))


def gen_project(project: str) -> Optional[List[Dict[str, Union[Path, str]]]]:
    """
    生成项目结构
    
    Args:
        project: 项目名称或路径
    
    Returns:
        Optional[List[Dict[str, Union[Path, str]]]]: 项目结构列表,如果项目已存在则返回None
    """
    path = Path(project) if is_path(project) else Path.cwd() / project

    if path.exists():
        raise Exception(f'{path.stem}项目已存在')

    return [
        {'path': path / 'spiders', 'type': 'dir'},
        {'path': path / 'models', 'type': 'dir'},
        {'path': path / 'utils', 'type': 'dir'},
        {'path': path / 'settings.py', 'type': 'file', 'text': read_template('settings')},
        {'path': path / 'middleware.py', 'type': 'file', 'text': read_template('middleware')},
        {'path': path / 'signals.py', 'type': 'file', 'text': read_template('signals')},
        {'path': path / 'README.md', 'type': 'file', 'text': read_template('README')},

        {'path': path / 'spiders/__init__.py', 'type': 'file', 'text': ''},

        {'path': path / 'models/__init__.py', 'type': 'file', 'text': ''},
        {'path': path / 'models/models.py', 'type': 'file', 'text': read_template('models')},

        {'path': path / 'utils/table.txt', 'type': 'file', 'text': ''},
        {'path': path / 'utils/curl.txt', 'type': 'file', 'text': ''},
    ]


def gen_spider(
        spider_name, url: str = None, source: Optional[str] = None, target: Optional[str] = None,
        help: Optional[str] = None
) -> str:
    """
    生成爬虫代码
    
    Args:
        name: 爬虫名称
        spider_name: 爬虫英文名称
        urls: 起始URL列表
        source: 数据源
        target: 目标
        help: 帮助信息
    
    Returns:
        str: 生成的爬虫代码
    """
    text = read_template('spider')
    text = text.replace('{{ name }}', spider_name)

    if url:
        start_req = f'''
        Request(
            url="{url}",
            target="{target}",
            help="{help}",
        )
        '''
        text = text.replace('{{ start_req }}', start_req)
    else:
        text = text.replace('''start_req_list = [
        {{ start_req }}
    ]\n''', '')

    if source:
        text = text.replace('{{ source }}', source)
    else:
        text = text.replace("source = '{{ source }}'\n", '')

    return text
