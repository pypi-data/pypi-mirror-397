from .spider import Spider

__all__ = ['DistributeSpider']


class DistributeSpider(Spider):

    def __init__(self, wait_timeout: int = 30, **kwargs):
        self.wait_timeout = wait_timeout
        super().__init__(**kwargs)

    def start(self):
        from AioSpider.core import DistributeEngine
        DistributeEngine(self).start()
