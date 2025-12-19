__all__ = [
    'utility_tools',
    'logger',
    '__version__'
]

import os
import sys
from pathlib import Path
from typing import Union

# 必须在任何 asyncio 操作之前切换事件循环策略
# 在 Windows 上，ProactorEventLoop 在程序退出时会导致 SSL 清理错误
# 切换到 SelectorEventLoop 可以避免 "_proactor is None" 错误
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from loguru import logger
from AioSpider.tools import utility_tools


logger.level1 = lambda msg: logger.debug(msg)
logger.level2 = lambda msg: logger.debug(msg)
logger.level3 = lambda msg: logger.info(msg)
logger.level4 = lambda msg: logger.warning(msg)
logger.level5 = lambda msg: logger.error(msg)
logger.level6 = lambda msg: logger.critical(msg)
logger.level7 = lambda msg: logger.critical(msg)


def get_package_name():
    from importlib.metadata import distribution
    try:
        return distribution('AioSpider-tarkin').metadata['Name']
    except Exception:
        return 'AioSpider-tarkin'


def get_version():
    from importlib.metadata import version
    try:
        return version(get_package_name())
    except Exception:
        # 如果包未安装，从 __version__ 文件读取
        from pathlib import Path
        version_file = Path(__file__).parent / '__version__'
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
        return '1.9.3'


__version__ = get_version()


def _get_work_path(path: Union[str, Path] = Path.cwd()):
     
    if isinstance(path, str):
        path = Path(path)

    if str(path) == str(path.anchor):
        return None

    if path.is_dir() and {'spiders', 'settings.py'} <= {i.name for i in path.iterdir()}:
        return path

    return _get_work_path(path.parent) or None


if sys.argv:
    try:
        path = _get_work_path(path=sys.argv[0])
    except RecursionError:
        path = Path.cwd()
else:
    print('sys args error!')
    exit(-1)

if path is not None:
    os.chdir(str(path))
    sys.path.append(str(path))


class TableView:

    def __init__(self, items, bold=True):
        self.items = items
        self.bold = bold
        self.colors = [
            'red', 'green', 'yellow', 'magenta', 'cyan',
            'white', 'orange3', 'purple3', 'turquoise4'
        ]

    def console(self):
        from rich.console import Console
        from rich.table import Table

        console = Console()

        # 创建表格
        table = Table(header_style="bold blue", border_style='#d2c1ad')

        for index, k in enumerate(self.items[0].keys()):
            style = 'bold ' + self.colors[index] if self.bold else self.colors[index]
            table.add_column(k, justify="left", style=style, no_wrap=True)
            # table.add_column("Age", justify="center", style="magenta")
            # table.add_column("City", justify="right", style="green")

        for v in self.items:
            table.add_row(*[str(i) for i in v.values()])

        # 输出表格
        console.print(table)
    