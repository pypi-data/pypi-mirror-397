#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AioSpider-tarkin Setup Script
用于构建和分发 AioSpider 爬虫框架
"""

from pathlib import Path
from setuptools import setup, find_packages


def read_version():
    """从 __version__ 文件读取版本号"""
    version_file = Path(__file__).parent / '__version__'
    if version_file.exists():
        return version_file.read_text(encoding='utf-8').strip()
    return '1.9.3'


def read_long_description():
    """读取长描述(README.md)"""
    readme_file = Path(__file__).parent / 'README.md'
    if readme_file.exists():
        return readme_file.read_text(encoding='utf-8')
    return ''


def read_requirements():
    """读取依赖列表"""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    if requirements_file.exists():
        with open(requirements_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []


# 包的元数据
PACKAGE_NAME = 'AioSpider-tarkin'
VERSION = read_version()
DESCRIPTION = '基于 asyncio 的高性能异步爬虫框架，支持 MySQL/MongoDB/Redis 等多种数据存储'
LONG_DESCRIPTION = read_long_description()
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
AUTHOR = 'Tarkin'
AUTHOR_EMAIL = ''
URL = 'https://github.com/yourusername/AioSpider-tarkin'  # 请替换为实际的项目地址
LICENSE = 'MIT'
PYTHON_REQUIRES = '>=3.8'

# 分类信息
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

KEYWORDS = [
    'spider', 'crawler', 'async', 'asyncio', 'aiohttp',
    'mysql', 'mongodb', 'redis', 'web scraping', 'data collection',
    '爬虫', '异步', '数据采集'
]

# 排除的包
EXCLUDE_PACKAGES = [
    'test_spider*',
    'cache*',
]

# 可选依赖（需要 C 编译环境或额外驱动的包）
EXTRAS_REQUIRE = {
    # 高性能字符编码检测（需要 C 编译）
    'cchardet': ['cchardet>=2.1.7'],

    # 数据库驱动（需要 C 编译或系统驱动）
    'mariadb': ['mariadb>=1.1.10'],
    'oracle': ['cx_Oracle>=8.3.0'],
    'postgresql': ['psycopg2-binary>=2.9.10', 'asyncpg>=0.30.0'],
    'sqlserver': ['pyodbc>=5.2.0', 'aioodbc>=0.5.0'],

    # 完整安装（包含所有可选依赖）
    'full': [
        'cchardet>=2.1.7',
        'mariadb>=1.1.10',
        'cx_Oracle>=8.3.0',
        'psycopg2-binary>=2.9.10',
        'asyncpg>=0.30.0',
        'pyodbc>=5.2.0',
        'aioodbc>=0.5.0',
    ],
}

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=['AioSpider'] + [f'AioSpider.{pkg}' for pkg in find_packages(exclude=EXCLUDE_PACKAGES)],
    package_dir={'AioSpider': '.'},
    include_package_data=True,
    package_data={
        '': [
            '__version__',
            'requirements.txt',
            'template/**/*',
            'resource/**/*',
            'notice/font/**/*',
        ],
    },
    install_requires=read_requirements(),
    extras_require=EXTRAS_REQUIRE,
    python_requires=PYTHON_REQUIRES,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    entry_points={
        'console_scripts': [
            # 主命令入口：安装后可以直接在命令行使用 aioSpider 命令
            'aioSpider=AioSpider.aioSpider:main',
        ],
    },
    zip_safe=False,
    project_urls={
        'Bug Reports': f'{URL}/issues',
        'Source': URL,
        'Documentation': URL,
    },
)
