import random
from AioSpider.tools import utility_tools


class BaseUser:
    
    def login(self):
        pass


class VisitorUser(BaseUser):
    """
    游客 从不需要登录得页面中提取或算法生成cookies
    """

    def __init__(self, custom_login=None, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.custom_login = custom_login
        self.kw = kwargs

    def login(self):
        if self.custom_login is None:
            return self.kw
        return self.custom_login(**self.kw)


class NormalUser(BaseUser):
    pass


class VipUser(BaseUser):
    pass
