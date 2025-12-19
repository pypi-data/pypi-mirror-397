from AioSpider.orm.fields import JSONField, CharField, BooleanField
from AioSpider.objects import UserType
from AioSpider.tools import dump_json_string

from .models import ABCModel

__all__ = ['UsersModel']


class UsersModel(ABCModel):
    """用户数据结构"""

    TYPE_CHOICES = (
        ('普通用户', UserType.normal), ('', UserType.visitor), ('vip用户', UserType.vip)
    )

    cookies = JSONField(name='cookies')
    username = CharField(name='用户名', max_length=50)
    password = CharField(name='密码', max_length=50)
    status = BooleanField(name='状态', default=True)
    # type = TinyIntField(name='类型 访客: 1, 普通用户: 2, vip用户: 3', choices=TYPE_CHOICES)

    order = ['cookies', 'username', 'password', 'status', 'type', 'source', 'create_time', 'update_time']

    @classmethod
    def get_users(cls, **kwargs) -> list:
        """获取访客用户"""
        return cls.filter(status=True, **kwargs).all()

    @classmethod
    def create_visitor(cls, cookies: dict):
        """创建访客用户"""
        return cls.objects.create(cookies=dump_json_string(cookies), type=UserType.visitor)

    @classmethod
    def create_normal_user(cls, username: str, password: str):
        """创建访客用户"""
        return cls.objects.create(username=username, password=password, type=UserType.normal)

    @classmethod
    def create_vip_user(cls, username: str, password: str):
        """创建访客用户"""
        return cls.objects.create(username=username, password=password, type=UserType.vip)
