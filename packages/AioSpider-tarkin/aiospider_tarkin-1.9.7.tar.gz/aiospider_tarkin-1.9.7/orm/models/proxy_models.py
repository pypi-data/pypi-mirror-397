import requests

from AioSpider.orm.fields import (
    CharField,
    BooleanField,
    FloatField,
    IntField,
    SmallIntField,
    DateField
)
from AioSpider.objects import TableType
from AioSpider.tools import extract_with_regex
from .models import ABCModel

__all__ = ['ProxyPoolModel']


class ProxyPoolModel(ABCModel):
    """IP代理池数据结构"""

    brand = CharField(name="代理服务商名称", max_length=50)
    ip = CharField(name="ip地址", max_length=20, null=False)
    port = SmallIntField(name="端口", null=False)
    protocol = CharField(name="ip协议", max_length=20, null=False)
    username = CharField(name="用户名", max_length=50)
    password = CharField(name="密码", max_length=50)
    status = BooleanField(name="ip是否可用", default=True)
    address = CharField(name="ip城市地址", max_length=20)
    operator = CharField(name="运营商", max_length=20)
    weight = FloatField(name="分配权重", null=False, default=0.1)
    use_count = IntField(name="使用次数", null=False, default=0)
    weekday = IntField(name="周一 ~ 周日，0开始，周一：0；周日：6", null=False, default=0)
    running = BooleanField(name="是否正在使用，1：正在使用，1：未使用", default=False)
    due_date = DateField(name="截止日期")
    remark1 = CharField(name="备注1", max_length=255)
    remark2 = CharField(name="备注2", max_length=255)
    remark3 = CharField(name="备注3", max_length=255)

    order = [
        'brand', 'ip', 'port', 'protocol', 'username', 'password', 'status', 'address', 'operator',
        'weight', 'use_count', 'weekday', 'running', 'due_date', 'remark1', 'remark2', 'remark3',
        'source', 'create_time', 'update_time'
    ]

    class Meta:
        table_type = TableType.proxy
    
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

        def get_ip_address(ip: str):
            res = requests.get(
                url=f'https://www.ip138.com/iplookup.asp?ip={ip}&action=2',
                headers={
                    "Referer": "https://www.ip138.com/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) C"
                                  "hrome/108.0.0.0 Safari/537.36"
                }
            )
            res.encoding = 'gbk'
            data = extract_with_regex(res.text, '"ASN归属地":"(.*?)"').strip().split()
            if len(data) >= 2:
                return data[:2]
            elif len(data) == 1:
                return data[0], None
            else:
                return None, None

        address, operator = get_ip_address(ip)

        return cls.objects.create(
            ip=ip, port=port, username=username, password=password, weight=weight, protocol=protocol, 
            brand=brand, address=address, operator=operator
        )
