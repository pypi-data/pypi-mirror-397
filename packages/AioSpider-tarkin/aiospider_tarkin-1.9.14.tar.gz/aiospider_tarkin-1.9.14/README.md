# AioSpider-tarkin

<div align="center">

[![PyPI version](https://badge.fury.io/py/AioSpider-tarkin.svg)](https://badge.fury.io/py/AioSpider-tarkin)
[![Python Version](https://img.shields.io/pypi/pyversions/AioSpider-tarkin.svg)](https://pypi.org/project/AioSpider-tarkin/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

基于 asyncio 的高性能异步爬虫框架

[特性](#核心特性) • [安装](#安装) • [快速开始](#快速开始) • [文档](#文档) • [示例](#示例)

</div>

---

## 核心特性

- ✅ **异步高并发**：基于 asyncio 的异步架构，支持高并发请求
- ✅ **多数据库支持**：内置 MySQL、SQLite、MongoDB、Redis、CSV 支持
- ✅ **强大的 ORM**：类似 Django ORM 的数据操作接口
- ✅ **中间件系统**：灵活的请求/响应处理中间件
- ✅ **数据去重**：支持布隆过滤器、集合等多种去重方式
- ✅ **智能并发控制**：多种并发策略（固定、随机、智能）
- ✅ **完整的日志系统**：支持控制台、文件、邮件、钉钉等多种输出
- ✅ **命令行工具**：丰富的 CLI 工具支持项目管理

## 安装

### 基础安装

```bash
pip install AioSpider-tarkin
```

### 可选依赖

AioSpider-tarkin 的核心功能无需 C 编译环境。以下是可选依赖的安装方式：

```bash
# 安装高性能字符编码检测（需要 C 编译环境）
pip install AioSpider-tarkin[cchardet]

# 安装 MariaDB 支持（需要 C 编译环境）
pip install AioSpider-tarkin[mariadb]

# 安装 Oracle 支持（需要 C 编译环境和 Oracle Instant Client）
pip install AioSpider-tarkin[oracle]

# 安装 PostgreSQL 支持（需要 C 编译环境）
pip install AioSpider-tarkin[postgresql]

# 安装 SQL Server 支持（需要 C 编译环境和 ODBC 驱动）
pip install AioSpider-tarkin[sqlserver]

# 安装所有可选依赖（需要 C 编译环境）
pip install AioSpider-tarkin[full]
```

**注意**：如果您的环境没有 C 编译器（如 Windows 上的 Microsoft Visual C++），建议只安装基础版本，框架会使用纯 Python 实现的替代包。

## 快速开始

### 1. 创建项目

```bash
# 创建新项目
aioSpider create -p myproject

# 进入项目目录
cd myproject
```

### 2. 创建爬虫

```python
# spiders/example_spider.py
from AioSpider.http import Request
from AioSpider.spider import Spider

class ExampleSpider(Spider):
    """示例爬虫"""

    name = '示例爬虫'
    source = '示例'

    def start_requests(self):
        """初始化请求"""
        yield Request(
            url='https://api.example.com/data',
            callback=self.parse
        )

    def parse(self, response):
        """解析响应"""
        data = response.json()
        # 处理数据...
        yield {'title': data['title']}

if __name__ == '__main__':
    spider = ExampleSpider()
    spider.start()
```

### 3. 配置数据库

```python
# settings.py
from AioSpider.objects import MysqlConnectionData

class DataBaseConfig:
    class Mysql:
        enabled = True
        connect = [
            MysqlConnectionData(
                alias='default',
                host="localhost",
                db="mydb",
                username="root",
                password="password",
                charset="utf8mb4",
            ),
        ]
```

### 4. 运行爬虫

```bash
# 方式1: 直接运行
python spiders/example_spider.py

# 方式2: 使用命令行运行
aioSpider crawl 示例爬虫
```

## 文档

详细文档请查看：
- [完整使用指南](AioSpider完整使用指南.md)
- API 文档（即将推出）

## 示例

### HTTP 请求示例

```python
from AioSpider.http import Request, FormRequest

# GET 请求
yield Request(
    url='https://api.example.com/search',
    params={'keyword': 'python'},
    callback=self.parse
)

# POST 请求
yield FormRequest(
    url='https://api.example.com/login',
    data={'username': 'user', 'password': 'pass'},
    callback=self.after_login
)
```

### 数据模型示例

```python
from AioSpider.orm import fields, MySQLModel

class ArticleModel(MySQLModel):
    """文章数据模型"""

    title = fields.CharField(name="标题", max_length=200)
    url = fields.CharField(name="链接", max_length=500, unique=True)
    content = fields.TextField(name="内容")
    publish_date = fields.DateField(name="发布日期")

    class Meta:
        alias = 'default'
        table_name = 't_articles'
```

### 响应解析示例

```python
def parse(self, response):
    # JSON 解析
    data = response.json()

    # JSONPath 解析
    items = response.parse_json('data.list', [])

    # XPath 解析
    titles = response.xpath('//h1/text()').getall()

    # CSS 选择器
    links = response.css('a::attr(href)').getall()
```

## 适用场景

- 大规模数据采集
- 定时数据更新
- API 数据爬取
- 数据监控和分析

## 技术栈

- **异步框架**: asyncio, aiohttp
- **数据库**: MySQL, MongoDB, Redis, SQLite
- **解析库**: lxml, BeautifulSoup4
- **日志系统**: loguru
- **数据处理**: pandas

## 系统要求

- Python >= 3.8
- Windows / Linux / macOS

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 作者

Tarkin

---

**如果觉得这个项目对您有帮助，请给一个 ⭐ Star 支持一下！**
