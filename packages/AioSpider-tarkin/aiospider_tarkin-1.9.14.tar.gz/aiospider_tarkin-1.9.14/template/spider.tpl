from AioSpider.http import Request
from AioSpider.spider import Spider


class {{ name }}(Spider):

    name = '{{ name }}'
    source = '{{ source }}'
    start_req_list = [
        {{ start_req }}
    ]

    def parse(self, response):
        pass


if __name__ == '__main__':
    spider = {{ name }}()
    spider.start()
