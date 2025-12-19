import time
import random
import inspect
from typing import Union, List

from AioSpider.tools import utility_tools
from AioSpider.objects import UserType, EventType
from AioSpider.orm import UsersModel

from .user import BaseUser, VisitorUser


class UserPool:

    def __init__(self, event_engine, users: Union[BaseUser, List[BaseUser]] = None, mode='random', reload_interval=300):
        self.mode = mode
        self.users = users or []
        self.cookies = []
        self.start_stamp = time.time()
        self.reload_interval = reload_interval
        self.user_model = UsersModel
        self._flag = False
        event_engine.register(EventType.spider_open, self.spider_open)
        event_engine.register(EventType.spider_close, self.spider_close)

    def spider_open(self, spider):

        users = spider.users

        if not users:
            return

        if isinstance(users, BaseUser):
            self.users = [users]
        if isinstance(users, list):
            self.users = users
        elif inspect.isclass(users, UsersModel):
            self.user_model = users
            self._flag = True
            self.reload()
        else:
            return 

    def reload(self):
        self.users.clear()
        for i in self.user_model.get_users():
            if i['type'] == UserType.visitor:
                self.users.append(VisitorUser(**utility_tools.load_json(i['cookies'])))
            elif i['type'] == UserType.normal:
                pass
            elif i['type'] == UserType.vip:
                pass
            else:
                continue
        self.start_stamp = time.time()

    def spider_close(self, spider):
        pass
        
    def get_random_user(self):
        return self.cookies[random.randint(0, len(self.cookies) - 1)]
    
    def get_user_cookies(self):

        if self._flag and (time.time() - self.start_stamp >= self.reload_interval):
            self.reload()

        if not self.users:
            return {}
        
        if not self.cookies:
            self.cookies = [user.login() for user in self.users]

        if self.mode == 'random':
            return self.get_random_user()

        return {}
