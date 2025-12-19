import requests

from AioSpider.tools import system_tools, utility_tools


address = f'http://{system_tools.get_ipv4()}:10010'


def create_notice(spider_name, message, level, platform, action, env):

    api = '/api/notice/create'
    data = {
        'spider_name': spider_name, 'datetime': utility_tools.get_relative_date(is_str=True), 'action': action,
        'level': level, 'platform': platform, 'message': message, 'env': env
    }
    try:
        res = requests.post(address + api, data=data, timeout=3)
        print(res.json())
    except requests.ConnectionError as e:
        print('AioServer 服务器连接失败!')
    except Exception as e:
        print(e)

