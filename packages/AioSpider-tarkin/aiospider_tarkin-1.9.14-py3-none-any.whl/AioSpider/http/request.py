from urllib.parse import urlparse
from typing import Optional, Callable, Union, Any, List

import requests
from retry import retry
from attr import define, field, fields
from attr.validators import instance_of, optional, or_
from w3lib.url import safe_url_string

from AioSpider.objects import HttpMethod, RequestStatus
from AioSpider.exceptions import RequestException
from AioSpider.tools import make_timestamp, encode_url_params, calculate_md5


def url_setattr(instance: "URL", attribute, value: str) -> str:
    """处理URL属性设置"""
    if ':' not in value:
        raise RequestException(f'无效的请求URL，URL: {value}')

    url = safe_url_string(value)
    parsed_url = urlparse(url)

    instance.scheme = parsed_url.scheme
    instance.domain = parsed_url.netloc
    instance.website = f"{instance.scheme}://{instance.domain}"
    instance.path = parsed_url.path

    return url


@define(kw_only=True, slots=True)
class URL:
    """URL对象封装类"""

    url: str = field(factory=str, validator=instance_of(str), on_setattr=url_setattr)
    scheme: str = field(default=None, validator=optional(instance_of(str)))
    domain: str = field(default=None, validator=optional(instance_of(str)))
    website: str = field(default=None, validator=optional(instance_of(str)))
    path: str = field(default=None, validator=optional(instance_of(str)))

    def __attrs_post_init__(self):
        url_setattr(self, self, self.url)

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        if not isinstance(other, URL):
            return NotImplemented
        return self.url == other.url


class Row:
    """基础行数据类"""

    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    def get(self, key, default=None):
        return self.value if key == self.key else default

    def to_dict(self):
        return {self.key: self.value}

    def __str__(self):
        return f"{self.key}={self.value}"

    __repr__ = __str__


class ItemRow(Row):
    """可变行数据类"""

    def __init__(self, key: str, value: Any):
        super().__init__(key, value)
        self.changed = False


class StampRow(Row):
    """时间戳行数据类"""

    def __init__(self, key: str = "_", value: int = make_timestamp()):
        super().__init__(key, value)
        self.changed = True


class Rows:
    """行数据集合类"""

    def __init__(self, *args, **kwargs):
        self.rows = []
        for row in args:
            self.append_row(row)
        for key, value in kwargs.items():
            self.append(key, value)

    def append_row(self, row: Row):
        if not isinstance(row, Row):
            raise ValueError('row must be a Row instance')
        self.rows.append(row)

    def append(self, key, value):
        self.rows.append(ItemRow(key, value))

    def get(self, key, default=None):
        for row in self.rows:
            value = row.get(key)
            if value is not None:
                return value
        return default

    def to_dict(self, changed: bool = None):
        if changed is None:
            return {row.key: row.value for row in self.rows}
        return {row.key: row.value for row in self.rows if row.changed is changed}

    def __bool__(self):
        return bool(self.rows)

    def __setitem__(self, key, value):
        self.append(key, value)

    def __getitem__(self, key):
        for row in self.rows:
            if row.key == key:
                return row.value
        raise KeyError(key)


def set_url(instance: "HttpRequest", attribute, value: Union[str, URL]) -> URL:
    """设置URL属性"""
    url_obj = URL(url=value) if isinstance(value, str) else value
    instance.update_hash(url_obj.url)
    return url_obj


def set_headers(instance: "HttpRequest", attribute, value: Union[dict, Rows]) -> Rows:
    """设置请求头"""
    headers = Rows(**value) if isinstance(value, dict) else value
    if not headers:
        from AioSpider.settings import SpiderRequestConfig
        headers = Rows(**SpiderRequestConfig.get_headers())

    if instance.auto_user_agent and not (headers.get('User-Agent') or headers.get('user-agent')):
        from AioSpider.settings import SpiderRequestConfig
        headers['User-Agent'] = SpiderRequestConfig.get_user_agent()

    if instance.auto_referer and not (headers.get('Referer') or headers.get('referer')):
        headers['Referer'] = instance.url.website

    return headers


def set_params(instance: "HttpRequest", attribute, value: Union[dict, Rows]) -> Rows:
    """设置URL参数"""
    params = Rows(**value) if isinstance(value, dict) else value
    instance.update_hash(params=params, json=instance.json, data=instance.data, url=instance.url.url)
    return params


def set_data(instance: "HttpRequest", attribute, value: Union[dict, Rows]) -> Rows:
    """设置表单数据"""
    data = Rows(**value) if isinstance(value, dict) else value
    instance.update_hash(data=data, json=instance.json, params=instance.params, url=instance.url.url)
    return data


def set_json(instance: "HttpRequest", attribute, value: Union[dict, Rows]) -> Rows:
    """设置JSON数据"""
    json = Rows(**value) if isinstance(value, dict) else value
    instance.update_hash(json=json, params=instance.params, data=instance.data, url=instance.url.url)
    return json


def set_cookies(instance: "HttpRequest", attribute, value: Union[dict, Rows]) -> Rows:
    """设置Cookie"""
    return Rows(**value) if isinstance(value, dict) else value


@define(kw_only=True, slots=True)
class HttpRequest:
    """HTTP请求基类"""

    _current_id = 0

    req_id: int = field(default=-1, init=False)
    url: Union[str, URL] = field(
        factory=str,
        validator=or_(instance_of(str), instance_of(URL)),
        on_setattr=set_url
    )
    method: HttpMethod = field(validator=instance_of(HttpMethod))
    callback: Optional[Callable[[Any], Any]] = field(default=None, validator=optional(instance_of(Callable)))
    headers: Optional[Union[dict, Rows]] = field(
        default=None,
        converter=lambda x: Rows(**x) if isinstance(x, dict) else x,
        validator=optional(instance_of(Rows)),
        on_setattr=set_headers
    )
    params: Optional[Union[dict, Rows]] = field(
        default=None,
        converter=lambda x: Rows(**x) if isinstance(x, dict) else x,
        validator=optional(instance_of(Rows)),
        on_setattr=set_params
    )
    data: Optional[Union[dict, Rows]] = field(
        default=None,
        converter=lambda x: Rows(**x) if isinstance(x, dict) else x,
        validator=optional(instance_of(Rows)),
        on_setattr=set_data
    )
    json: Optional[Union[dict, Rows]] = field(
        default=None,
        converter=lambda x: Rows(**x) if isinstance(x, dict) else x,
        validator=optional(instance_of(Rows)),
        on_setattr=set_json
    )
    cookies: Optional[Union[dict, Rows]] = field(
        default=None,
        converter=lambda x: Rows(**x) if isinstance(x, dict) else x,
        validator=optional(instance_of(Rows)),
        on_setattr=set_cookies
    )
    timeout: Optional[int] = field(default=None, validator=optional(instance_of(int)))
    proxy: Optional[str] = field(default=None, validator=optional(instance_of(str)))
    encoding: Optional[staticmethod] = field(default=None, validator=optional(instance_of(str)))
    priority: int = field(default=1, validator=instance_of(int))
    dnt_filter: bool = field(default=False, validator=instance_of(bool))
    help: Optional[str] = field(default=None, validator=optional(instance_of(str)))
    auto_user_agent: bool = field(default=True, validator=instance_of(bool))
    auto_referer: bool = field(default=True, validator=instance_of(bool))
    render: bool = field(default=False, validator=instance_of(bool))
    max_retries: int = field(default=3, validator=instance_of(int))
    meta: dict = field(factory=dict)
    time: int = field(default=0, validator=instance_of(int))
    status: RequestStatus = field(default=RequestStatus.before, validator=instance_of(RequestStatus))
    hash: Optional[str] = field(default=None, validator=optional(instance_of(str)))

    _retry_times: int = field(default=0, validator=instance_of(int))
    _retry_status: int = field(
        factory=tuple, converter=tuple, validator=instance_of(tuple)
    )

    def __attrs_post_init__(self):
        """初始化请求ID和重试配置"""
        HttpRequest._current_id += 1
        self.req_id = HttpRequest._current_id
        self.url = set_url(self, fields(cls=self.__class__).url, self.url)
        self.headers = set_headers(self, fields(cls=self.__class__).headers, self.headers)
        self.params = set_params(self, fields(cls=self.__class__).params, self.params)
        self.data = set_data(self, fields(cls=self.__class__).data, self.data)
        self.json = set_json(self, fields(cls=self.__class__).json, self.json)
        self.cookies = set_cookies(self, fields(cls=self.__class__).cookies, self.cookies)
        self.update_hash(url=self.url.url, params=self.params, data=self.data, json=self.json)
        self._init_retry()

    def __hash__(self):
        return hash(self.hash or self.req_id)

    def __eq__(self, other):
        if not isinstance(other, HttpRequest):
            return NotImplemented
        return self.hash == other.hash or self.req_id == other.req_id

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        separator = "=" * 80
        request_info = f"Request: {self.help or ''} {self.method.value}"
        details = [
            f"URL: {self.url.url}",
            f"Headers: {self.headers.to_dict() if self.headers else self.headers}",
            f"Params: {self.params.to_dict() if self.params else self.params}",
            f"Data: {self.data.to_dict() if self.data else self.data}",
            f"JSON: {self.json.to_dict() if self.json else self.json}",
            f"Cookies: {self.cookies.to_dict() if self.cookies else self.cookies}",
            f"Timeout: {self.timeout}",
            f"Proxy: {self.proxy}"
        ]
        formatted_details = "\n".join(f"  {item}" for item in details)
        return f"{separator}\n{request_info}\n{formatted_details}\n{separator}"

    __repr__ = __str__

    def _init_retry(self):
        """初始化重试配置"""
        from AioSpider.settings import SpiderRequestConfig
        self.max_retries = SpiderRequestConfig.MAX_STATUS_RETRY_TIMES or self.max_retries
        self._retry_status = self._retry_status or SpiderRequestConfig.RETRY_STATUS

    def retry(self, status: int) -> bool:
        """判断是否需要重试请求"""
        if self._retry_times < self.max_retries and status in self._retry_status:
            self._retry_times += 1
            return True
        return False

    def clone(self, **kwargs) -> "HttpRequest":
        """克隆请求对象"""
        new_attrs = {field.name: getattr(self, field.name) for field in fields(self.__class__)}
        new_attrs.update(kwargs)
        return self.__class__(**new_attrs)

    def fetch(self):
        """发送同步请求"""
        request_kwargs = self.to_request_dict()
        request_kwargs['proxies'] = self._get_proxy_dict()
        request_kwargs.pop('proxy')
        return requests.request(**request_kwargs)

    def _get_proxy_dict(self) -> Optional[dict]:
        """获取代理配置字典"""
        return {'http': self.proxy, 'https': self.proxy} if self.proxy else None

    def update_hash(self, url: str = None, params: Rows = None, data: Rows = None, json: Rows = None):
        """更新请求哈希值"""
        components = [
            url or self.url.url,
            encode_url_params(params.to_dict(changed=False) if params else {}),
            encode_url_params(data.to_dict(changed=False) if data else {}),
            encode_url_params(json.to_dict(changed=False) if json else {})
        ]
        self.hash = calculate_md5('-'.join(components))

    def to_request_dict(self) -> dict:
        """转换为请求字典格式"""
        return {
            'url': self.url.url,
            'method': self.method.value,
            'headers': self.headers.to_dict() if self.headers else self.headers,
            'params': self.params.to_dict() if self.params else self.params,
            'data': self.data.to_dict() if self.data else self.data,
            'json': self.json.to_dict() if self.json else self.json,
            'cookies': self.cookies.to_dict() if self.cookies else self.cookies,
            'timeout': self.timeout,
            'proxy': self.proxy
        }


class BaseRequest(HttpRequest):
    """请求类基类,提供了创建和管理HTTP请求的基础功能"""

    method: HttpMethod
    _retry_decorator = retry(tries=3, delay=1.0, backoff=2.0)

    def __new__(
            cls, url: str, headers: dict = None, params: dict = None, data: dict = None, json: dict = None,
            cookies: dict = None, callback=None, retry_policy: dict = None, **kwargs
    ):
        attr_names = set(i.name for i in fields(cls))
        meta = {k: v for k, v in kwargs.items() if k not in attr_names}

        # 处理重试策略
        if retry_policy:
            meta['retry_policy'] = retry_policy

        return HttpRequest(
            url=URL(url=url),
            method=cls.method,
            headers=headers,
            params=params,
            data=data,
            json=json,
            cookies=cookies,
            callback=callback,
            meta=meta,
            **{i: kwargs.get(i) for i in kwargs if i in attr_names}
        )

    @classmethod
    def from_dict(cls, **kwargs):
        """从字典创建请求对象"""
        return cls(**kwargs)

    @classmethod
    def from_url(cls, url: str, **kwargs) -> "BaseRequest":
        """从URL创建请求对象"""
        return cls(url=url, **kwargs)

    @classmethod
    def from_urls(cls, urls: List[str], **kwargs) -> List["BaseRequest"]:
        """从URL列表创建请求对象"""
        return [cls(url=url, **kwargs) for url in urls]

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {field.name: getattr(self, field.name) for field in fields(self.__class__)}

    @classmethod
    def create_batch(cls, urls: List[str], **kwargs) -> List["BaseRequest"]:
        """批量创建请求对象

        Args:
            urls: URL列表
            **kwargs: 其他请求参数
        """
        return [cls(url=url, **kwargs) for url in urls]

    @classmethod
    def with_retry(cls, *args, **kwargs) -> "BaseRequest":
        """创建带重试机制的请求对象"""
        request = cls(*args, **kwargs)
        request.fetch = cls._retry_decorator(request.fetch)
        return request


class Request(BaseRequest):
    """GET请求"""
    method = HttpMethod.GET


class FormRequest(BaseRequest):
    """POST请求"""
    method = HttpMethod.POST
