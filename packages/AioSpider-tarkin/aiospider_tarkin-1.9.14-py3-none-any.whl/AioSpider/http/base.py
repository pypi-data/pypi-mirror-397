import json
from urllib.parse import urlparse
from typing import Literal, Optional, Callable, Union

import requests
from w3lib.url import safe_url_string

from AioSpider.exceptions import RequestException, StatusTags
from AioSpider.tools.tools import deepcopy
from AioSpider.tools.network_tools import quote_url, quote_params
from AioSpider.tools.encrypt_tools import make_md5


RequestMethod = Literal['GET', 'POST']


class BaseRequest(object):
    """ 实现请求方法 """

    __slots__ = (
        '_url', 'scheme', 'domain', 'website', 'path', 'method', 'headers', '_params', '_data', 'callback', 'cookies', 
        'timeout', 'proxy', 'encoding', 'priority', 'dnt_filter', 'help', 'auto_referer', 'meta', '_hash', 'render',
        'depth', 'times', 'time'
    )
    _default_value = {
        'method': 'GET', 'callback': None, '_params': None, 'headers': None, 'encoding': None, '_data': None,
        'cookies': None, 'timeout': None, 'proxy': None, 'priority': 1, 'dnt_filter': False, 'help': None,
        'add_headers': None, 'target': None, 'auto_referer': True, 'render': False, 'depth': 0, 'times': 0,
        'time': None
    }
    _filters = ['scheme', 'domain', 'website', 'path', 'target', '_hash']

    def __init__(
            self, url: str, method: RequestMethod = 'GET', callback: Optional[Callable] = None,
            params: Optional[dict] = None, headers: Optional[dict] = None, encoding: str = None,
            data: Union[dict, str] = None, cookies: Optional[dict] = None, timeout: Optional[int] = None,
            proxy: Optional[str] = None, priority: int = 1, dnt_filter: bool = False, help: Optional[str] = None,
            add_headers: Optional[dict] = None, target: str = None, auto_referer=True, render=False, depth=0, 
            times: int = 0, **kwargs
    ):

        self._url = self._set_url(url, encoding)
        self.scheme = urlparse(self._url).scheme
        self.domain = urlparse(self._url).netloc
        self.website = f"{self.scheme}://{self.domain}"
        self.path = urlparse(self._url).path
        self.method = method.upper()
        self.headers = headers
        self._params = params
        self._data = data
        self.cookies = cookies
        self.timeout = timeout
        self.proxy = proxy
        self.encoding = encoding
        self.callback = callback
        self.dnt_filter = dnt_filter
        self.priority = priority
        self.auto_referer = auto_referer
        self.help = help
        self.meta = {}
        self._hash = None
        self.render = render
        self.depth = depth
        self.times = times
        self.time = 0

        if add_headers is not None:
            self.headers.update(add_headers)

        for k in kwargs:
            self.meta[k] = kwargs[k]
    
    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, url):
        self._url = url
        self.scheme = urlparse(self._url).scheme
        self.domain = urlparse(self._url).netloc
        self.website = f"{self.scheme}://{self.domain}"
        self.path = urlparse(self._url).path
        self._hash = None

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        self._hash = None
        
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._hash = None

    def _set_url(self, url, encoding):
        """网址的修正以及判断"""
        assert isinstance(url, str) and ':' in url, RequestException(status=StatusTags.InvalidRequestURL)
        return safe_url_string(url, encoding or 'utf-8')
 
    def fetch(self):
        proxies = {
            'http': self.proxy, 'https': self.proxy
        }
        if self.method.upper() == 'GET':
            return requests.get(
                self.url, headers=self.headers, params=self.params, proxies=proxies, cookies=self.cookies, 
                timeout=self.timeout
            )
        if self.method.upper() == 'POST':
            return requests.post(
                self.url, headers=self.headers, params=self.params, data=self.data, cookies=self.cookies, 
                proxies=proxies, timeout=self.timeout
            )

    def __str__(self):
        if self.help:
            return f"Request {self.time} ms <{self.help} {self.method} {self.url}>"
        return f"<{self.method} {self.url}>"

    __repr__ = __str__

    def __getattr__(self, item):
        if item in self.__slots__:
            return self.__dict__[item]
        return self.meta.get(item, None)

    def __lt__(self, other):
        return self.priority < other.priority

    @property
    def hash(self):
        
        if self._hash is None:

            def remove_exclude_stamps(data_dict):
                if exclude_stamp:
                    return {k: v for k, v in data_dict.items() if k not in settings.RequestFilterConfig.ExcludeStamp}
                return data_dict

            from AioSpider import settings

            exclude_stamp = settings.RequestFilterConfig.IgnoreStamp and settings.RequestFilterConfig.ExcludeStamp

            url = self.url
            if self.params:
                params = remove_exclude_stamps(self.params)
                url = quote_url(url, params)

            if isinstance(self.data, str):
                try:
                    data = json.loads(self.data)
                except:
                    data = self.data
            else:
                data = deepcopy(self.data or {})
            
            if isinstance(data, dict):
                data = remove_exclude_stamps(data)
                self._hash = make_md5(f'{url}-{self.method}-{quote_params(data)}')
            else:
                self._hash = make_md5(f'{url}-{self.method}-{data}')

        return self._hash

    def to_dict(self):
        request_dict = {}
        for slot in self.__slots__:
            value = getattr(self, slot)
            if slot in self._filters:
                continue
            if callable(value):
                value = value.__name__
            if value != self._default_value.get(slot):
                request_dict[slot.lstrip('_')] = value
        return request_dict

    @classmethod
    def from_dict(cls, request_dict):
        request_dict['_hash'] = None
        return cls(**{**request_dict.pop('meta'), **request_dict})
