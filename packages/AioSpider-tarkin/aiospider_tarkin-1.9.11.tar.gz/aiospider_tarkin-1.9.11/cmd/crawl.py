import sys
import importlib
import inspect
from pathlib import Path
from typing import Optional

from .cmd import AioSpiderCommand


class CrawlCommand(AioSpiderCommand):
    """
    运行爬虫的命令
    用法: aioSpider crawl <爬虫名称>
    """

    def __init__(self):
        super().__init__()
        self.spider_name: Optional[str] = None

    def add_name(self, name):
        """添加爬虫名称"""
        if not self.spider_name:
            self.spider_name = str(name)

    def _find_spider_directory(self):
        """
        查找 spider 目录
        从当前目录开始向上查找,直到找到包含 spider 目录的路径
        """
        current_dir = Path.cwd()

        # 首先检查当前目录
        spider_dir = current_dir / 'spiders'
        if spider_dir.exists() and spider_dir.is_dir():
            return spider_dir

        # 向上查找最多3级目录
        for parent in [current_dir.parent, current_dir.parent.parent]:
            spider_dir = parent / 'spiders'
            if spider_dir.exists() and spider_dir.is_dir():
                return spider_dir

        return None

    def _auto_discover_spiders(self, spider_dir):
        """
        自动发现 spider 目录下的所有爬虫类
        递归扫描所有子文件夹下的 .py 文件并导入其中的 Spider 类
        """
        from AioSpider.spider import Spider

        discovered_spiders = []

        print(f'正在递归扫描 spiders 目录: {spider_dir}')

        # 递归遍历 spider 目录及其所有子目录下的 .py 文件
        for py_file in spider_dir.glob('**/*.py'):
            if py_file.name.startswith('__'):
                continue

            # 计算相对于 spider_dir 的相对路径
            relative_path = py_file.relative_to(spider_dir)

            # 将路径转换为模块名: spiders.subfolder.filename
            # 例如: spiders/东方财富/股票列表.py -> spiders.东方财富.股票列表
            parts = list(relative_path.parts[:-1]) + [relative_path.stem]
            module_name = 'spiders.' + '.'.join(parts)

            print(f'尝试导入模块: {module_name} (文件: {relative_path})')

            try:
                # 动态导入模块
                module = importlib.import_module(module_name)
                print(f'  成功导入模块: {module_name}')

                # 查找模块中的 Spider 类
                for attr_name in dir(module):
                    if attr_name.startswith('__'):
                        continue

                    attr = getattr(module, attr_name)

                    # 检查是否是 Spider 子类
                    if inspect.isclass(attr) and issubclass(attr, Spider) and attr is not Spider:
                        spider_name = getattr(attr, 'name', attr.__name__)
                        print(f'  找到爬虫: {attr.__name__} (name={spider_name})')
                        discovered_spiders.append(attr)
            except Exception as e:
                # 显示导入错误信息
                print(f'  导入失败: {e}')
                import traceback
                traceback.print_exc()

        print(f'共发现 {len(discovered_spiders)} 个爬虫')
        return discovered_spiders

    def execute(self):
        """执行 crawl 命令"""
        if not self.spider_name:
            print('错误: 请指定要运行的爬虫名称')
            print('用法: aioSpider crawl <爬虫名称>')
            print('示例: aioSpider crawl MySpider')
            return

        # 查找 spider 目录并添加到 sys.path
        spider_dir = self._find_spider_directory()
        if not spider_dir:
            print('错误: 没有找到 spiders 目录，请确保在项目根目录下运行此命令')
            print(f'当前工作目录: {Path.cwd()}')
            return

        # 将项目根目录添加到 sys.path
        project_root = spider_dir.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            print(f'已将项目根目录添加到 Python 路径: {project_root}')

        # 自动发现所有爬虫
        discovered_spiders = self._auto_discover_spiders(spider_dir)

        # 查找匹配的爬虫类
        spider_class = None
        for spider in discovered_spiders:
            # 方式1: 类名匹配 (不区分大小写)
            if spider.__name__.lower() == self.spider_name.lower():
                spider_class = spider
                break

            # 方式2: name 属性匹配 (如果有定义)
            if hasattr(spider, 'name') and spider.name and spider.name.lower() == self.spider_name.lower():
                spider_class = spider
                break

        if not spider_class:
            print(f'错误: 未找到名为 "{self.spider_name}" 的爬虫')
            print(f'\n可用的爬虫列表:')
            self._list_discovered_spiders(discovered_spiders)
            return

        # 实例化并启动爬虫
        try:
            print(f'正在启动爬虫: {self.spider_name}')
            spider_instance = spider_class()
            spider_instance.start()
        except Exception as e:
            print(f'启动爬虫时出错: {e}')
            import traceback
            traceback.print_exc()

    def _find_spider_class(self, spider_module):
        """
        在 spider 模块中查找指定名称的爬虫类
        支持两种匹配方式:
        1. 类名匹配 (例如: MySpider)
        2. spider.name 属性匹配 (例如: my_spider)
        """
        from AioSpider.spider import Spider

        # 遍历 spider 模块中的所有属性
        for attr_name in dir(spider_module):
            if attr_name.startswith('__'):
                continue

            attr = getattr(spider_module, attr_name)

            # 检查是否是类且继承自 Spider
            if inspect.isclass(attr) and issubclass(attr, Spider) and attr is not Spider:
                # 方式1: 类名匹配 (不区分大小写)
                if attr.__name__.lower() == self.spider_name.lower():
                    return attr

                # 方式2: name 属性匹配 (如果有定义)
                if hasattr(attr, 'name') and attr.name and attr.name.lower() == self.spider_name.lower():
                    return attr

        return None

    def _list_available_spiders(self, spider_module):
        """列出所有可用的爬虫 (旧方法,保留兼容性)"""
        from AioSpider.spider import Spider

        spiders = []
        for attr_name in dir(spider_module):
            if attr_name.startswith('__'):
                continue

            attr = getattr(spider_module, attr_name)

            if inspect.isclass(attr) and issubclass(attr, Spider) and attr is not Spider:
                spider_name = getattr(attr, 'name', attr.__name__)
                spider_desc = getattr(attr, 'description', '')
                spiders.append({
                    'name': spider_name,
                    'class': attr.__name__,
                    'description': spider_desc
                })

        if not spiders:
            print('  (未找到任何爬虫)')
            return

        for spider in spiders:
            desc = f' - {spider["description"]}' if spider['description'] else ''
            print(f'  - {spider["name"]} (类名: {spider["class"]}){desc}')

    def _list_discovered_spiders(self, discovered_spiders):
        """列出自动发现的所有爬虫"""
        if not discovered_spiders:
            print('  (未找到任何爬虫)')
            return

        spiders = []
        for spider_class in discovered_spiders:
            spider_name = getattr(spider_class, 'name', spider_class.__name__)
            spider_desc = getattr(spider_class, 'description', '')
            spiders.append({
                'name': spider_name,
                'class': spider_class.__name__,
                'description': spider_desc
            })

        for spider in spiders:
            desc = f' - {spider["description"]}' if spider['description'] else ''
            print(f'  - {spider["name"]} (类名: {spider["class"]}){desc}')


def crawl_cli():
    """
    命令行入口: aiospider-crawl <爬虫名称>
    用于通过 entry_points 直接启动爬虫
    """
    import sys

    if len(sys.argv) < 2:
        print('用法: aiospider crawl <爬虫名称>')
        print('示例: aiospider crawl MySpider')
        sys.exit(1)

    spider_name = sys.argv[1]

    # 创建 CrawlCommand 实例并执行
    from AioSpider.cmd import CommandName
    command = CrawlCommand()
    command.add_name(CommandName(spider_name))
    command.execute()
