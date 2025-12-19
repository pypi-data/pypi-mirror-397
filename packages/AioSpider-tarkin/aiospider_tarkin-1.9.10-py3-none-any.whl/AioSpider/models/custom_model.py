import re
from typing import List

import requests
from pandas import DataFrame

from AioSpider import field
from AioSpider.tools import tools
from AioSpider.constants import UserType
from AioSpider.tools.table_tools import (
    ExtractImageTable, extract_table_from_pdf, extract_table_from_xlsx, concat
)
from .models import ABCModel, FileModel


class PdfFileModel(FileModel):
    """PDF 文件数据结构"""

    extension = field.ExtensionNameField(name='拓展名', default='pdf')

    def extract_table(self, path):
        tables = extract_table_from_pdf(path, pages='all', encoding=self.Meta.encoding)

        if not tables:
            return None

        df = self.concat_table(tables)
        df = self.process_dataframe(df)

        yield from self.yield_dataframe(df)

    def process_raw_table(self, tables: List[DataFrame]) -> List[DataFrame]:
        return tables

    def concat_table(self, tables: List[DataFrame]) -> DataFrame:
        tables = self.process_raw_table(tables)
        new_tables = [self.process_raw_dataframe(table) for table in tables]
        return concat(new_tables)


class XlsxFileModel(FileModel):
    """XLXS 文件数据结构"""

    extension = field.ExtensionNameField(name='拓展名', default='xlsx')

    def extract_table(self, path):
        df = extract_table_from_xlsx(path)
        df = self.process_raw_dataframe(df)
        df = self.process_dataframe(df)

        yield from self.yield_dataframe(df)


class ImageModel(FileModel):
    """图片文件数据结构"""

    extension = field.ExtensionNameField(name='拓展名', default='png')

    def extract_table(self, path):
        df = ExtractImageTable(path)
        df = self.process_raw_dataframe(df)
        df = self.process_dataframe(df)

        yield from self.yield_dataframe(df)


class TablesModel(ABCModel):
    """表数据结构"""

    name = field.CharField(name='表名', max_length=50, unique=True)
    model = field.CharField(name='数据结构名', max_length=50)
    spider = field.CharField(name='爬虫名称', max_length=20)
    mark = field.CharField(name='备注', max_length=255)


class AiospiderModel(ABCModel):
    """AioSpider总表数据结构"""

    name = field.CharField(name='表名')
    db = field.DateTimeField(name='库名')
    status = field.BoolField(name='表状态。0：废弃，1：正常', default=True)

    order = [
        'id', 'name', 'db', 'status', 'source', 'create_time', 'update_time'
    ]


class SpiderModel(ABCModel):
    """爬虫数据结构"""

    SPIDER_STATUS_TYPE = (
        ('未开始', 0), ('进行中', 1), ('成功', 2), ('异常', 3),
    )
    DEV_STATUS_TYPE = (
        ('开发中', 0), ('测试中', 1), ('已上线', 2), ('维护中', 3), ('已废弃', 4)
    )
    RUN_LEVEL_TYPE = (
        ('秒级', 0), ('分级', 1), ('时级', 2), ('日级', 3), ('周级', 4), ('月级', 5),
        ('季级', 6), ('年级', 7)
    )

    # site = models.ForeignKey(
    #     SiteModel, on_delete=models.SET_NULL, verbose_name='所属站点', db_column='site',
    #     null=True, blank=True, related_name='spider'
    # )
    name = field.CharField(name='爬虫名称', max_length=20, null=False, unique=True)
    target = field.CharField(name='目标页面', max_length=255, null=False)
    description = field.TextField(name='描述', null=True)
    status = field.TinyIntField(name='运行状态', choices=SPIDER_STATUS_TYPE, default=0)
    dev_status = field.TinyIntField(name='开发状态', choices=DEV_STATUS_TYPE, default=0)
    start_time = field.TimeField(name='启动时间', default=None)
    last_run_time = field.DateTimeField(name='最近运行时间', default=None, null=True)
    level = field.TinyIntField(name='运行级别', choices=RUN_LEVEL_TYPE, default=0)
    count = field.IntField(name='运行次数', default=0)
    interval = field.MediumIntField(name='时间间隔')
    version = field.CharField(name='版本号', max_length=120, default='1.0')

    order = [
        'id', 'name', 'target', 'description', 'status', 'dev_status', 'start_time', 'last_run_time',
        'level', 'count', 'interval', 'version', 'source', 'create_time', 'update_time'
    ]


class TaskModel(ABCModel):
    """批次爬虫任务数据结构"""

    TASK_STATUS_TYPE = (
        ('未开始', 0), ('进行中', 1), ('成功', 2), ('异常', 3),
    )

    spider = field.CharField(name='爬虫名称', max_length=150)
    start_time = field.DateTimeField(name='启动时间')
    end_time = field.DateTimeField(name='结束时间')
    status = field.TinyIntField(name='任务状态', choices=TASK_STATUS_TYPE, default=0)
    data_count = field.IntField(name='数据条数', default=0)
    running_time = field.IntField(name='运行时间(s)', default=0)
    success_request_count = field.IntField(name='成功请求数量', default=0)
    failure_request_count = field.IntField(name='失败请求数量', default=0)

    order = [
        'id', 'spider', 'start_time', 'end_time', 'status', 'data_count', 'running_time',
        'success_request_count', 'failure_request_count', 'source', 'create_time', 'update_time'
    ]


class ProxyPoolModel(ABCModel):
    """IP代理池数据结构"""

    brand = field.CharField(name="代理服务商名称", max_length=50)
    ip = field.CharField(name="ip地址", max_length=20, null=False)
    port = field.SmallIntField(name="端口", null=False)
    protocol = field.CharField(name="ip协议", max_length=20, null=False)
    username = field.CharField(name="用户名", max_length=50)
    password = field.CharField(name="密码", max_length=50)
    status = field.BoolField(name="ip是否可用", default=True)
    address = field.CharField(name="ip城市地址", max_length=20)
    operator = field.CharField(name="运营商", max_length=20)
    weight = field.FloatField(name="分配权重", null=False, default=0.1)
    use_count = field.IntField(name="使用次数", null=False, default=0)
    weekday = field.IntField(name="周一 ~ 周日，0开始，周一：0；周日：6", null=False, default=0)
    running = field.BoolField(name="是否正在使用，1：正在使用，1：未使用", default=False)
    due_date = field.DateField(name="截止日期")
    remark1 = field.CharField(name="备注1", max_length=255)
    remark2 = field.CharField(name="备注2", max_length=255)
    remark3 = field.CharField(name="备注3", max_length=255)

    order = [
        'brand', 'ip', 'port', 'protocol', 'username', 'password', 'status', 'address', 'operator',
        'weight', 'use_count', 'weekday', 'running', 'due_date', 'remark1' 'remark2', 'remark3',
        'source', 'create_time', 'update_time'
    ]
    
    @classmethod
    def get_proxy(cls, **kwargs) -> list:
        """获取访客用户"""
        return cls.filter(status=True, **kwargs).all()

    @classmethod
    def create_proxy(
            cls, ip: str, port: int, username: str = None, password: str = None, weight: float = None,
            protocol: str = 'http', brand=None
    ):
        """创建访客用户"""

        def get_ip_address(ip):
            res = requests.get(
                url=f'https://www.ip138.com/iplookup.asp?ip={ip}&action=2',
                headers={
                    "Referer": "https://www.ip138.com/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) C"
                                  "hrome/108.0.0.0 Safari/537.36"
                }
            )
            res.encoding = 'gbk'
            data = tools.re_text(res.text, '"ASN归属地":"(.*?)"').strip().split()
            if len(data) >= 2:
                return data[:2]
            elif len(data) == 1:
                return data[0], None
            else:
                return None, None

        address, operator = get_ip_address(ip)

        return cls.create(
            ip=ip, port=port, username=username, password=password, weight=weight, protocol=protocol, 
            brand=brand, address=address, operator=operator
        )


class NoticeModel(ABCModel):

    LEVEL_CHOICES = (
        ('调试', 'DEBUG'), ('信息', 'INFO'), ('警告', 'WARNING'), ('异常', 'DEBUG'), ('崩溃', 'DANGEROUS')
    )
    TYPE_CHOICES = (
        ('通知', 'NOTICE'), ('预警', 'WARNING')
    )
    PLATFORM_CHOICES = (
        ('企业微信', 'WECHAT'), ('钉钉', 'DINGDING'), ('邮件', 'EMAIL')
    )

    # spider = field.ForeignKey(
    #     'spider.SpiderModel', on_delete=models.CASCADE, verbose_name='所属爬虫', related_name='notice',
    #     null=True, blank=True
    # )
    level = field.CharField('等级', max_length=20, choices=LEVEL_CHOICES, default='INFO')
    type = field.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='INFO')
    platform = field.CharField('平台', max_length=20, choices=PLATFORM_CHOICES, default='WECHAT')
    message = field.CharField('消息', max_length=20, )

    # class Meta:
    #     db_table = 'notice'
    #     verbose_name = '消息预警'
    #     verbose_name_plural = '预警类型'


class UsersModel(ABCModel):
    """用户数据结构"""

    TYPE_CHOICES = (
        ('普通用户', UserType.normal), ('', UserType.visitor), ('vip用户', UserType.vip)
    )
    
    cookies = field.JSONField(name='cookies')
    username = field.CharField(name='用户名', max_length=50)
    password = field.CharField(name='密码', max_length=50)
    status = field.BoolField(name='状态', default=True)
    type = field.TinyIntField(name='类型 访客: 1, 普通用户: 2, vip用户: 3', choices=TYPE_CHOICES)

    order = ['cookies', 'username', 'password', 'status', 'type', 'source', 'create_time', 'update_time']

    @classmethod
    def get_users(cls, **kwargs) -> list:
        """获取访客用户"""
        return cls.filter(status=True, **kwargs).all()

    @classmethod
    def create_visitor(cls, cookies: dict):
        """创建访客用户"""
        return cls.create(cookies=tools.dump_json(cookies), type=UserType.visitor)

    @classmethod
    def create_normal_user(cls, username: str, password: str):
        """创建访客用户"""
        return cls.create(username=username, password=password, type=UserType.normal)

    @classmethod
    def create_vip_user(cls, username: str, password: str):
        """创建访客用户"""
        return cls.create(username=username, password=password, type=UserType.vip)
