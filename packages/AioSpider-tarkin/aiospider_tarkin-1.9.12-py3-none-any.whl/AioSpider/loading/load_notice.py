__all__ = ['LoadNotice']

from AioSpider import message
from AioSpider.constants import NoticeType


class LoadNotice:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        instance.init_robot()

    def __init__(self, spider, settings):
        self.spider = spider
        self.settings = settings

    def init_robot(self):
        
        message.set_spider_name(self.spider)
        
        robot_config = {
            i: getattr(self.settings, i) for i in dir(self.settings)
            if not i.startswith('__') and not i.endswith('__')
        }

        for name, config in robot_config.items():

            if not config.get('enabled', False):
                continue

            if config.get('type') == NoticeType.platform:
                message.add_platform_robot(
                    name, spider=self.spider, config={k: v for k, v in config.items()}
                )
            if config.get('type') == NoticeType.wechat:
                message.add_wechat_robot(
                    name, spider=self.spider, config={k: v for k, v in config.items()}
                )
            if config.get('type') == NoticeType.dingding:
                message.add_dingding_robot(
                    name, spider=self.spider, config={k: v for k, v in config.items()}
                )
            if config.get('type') == NoticeType.email:
                message.add_email_robot(
                    name, spider=self.spider, config={k: v for k, v in config.items()}
                )
