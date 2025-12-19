import platform
from typing import Optional, Any, Union, List
from pathlib import Path

from attr import define, field, fields
from attr.validators import instance_of, optional
try:
    from cchardet import detect
except ImportError:
    from chardet import detect

from AioSpider.objects import By, RequestStatus
from AioSpider.browser import Browser
from AioSpider.parse import Parser
from AioSpider.exceptions import AioException
from AioSpider.tools import parse_json_data, open_in_browser

from .request import HttpRequest


def text_setter(instance: "Response", attribute: str, value: str) -> str:
    """设置text属性时同时更新parser"""
    instance.parser = Parser(value)
    instance._cached_data = {}
    return value


@define(kw_only=True, slots=True)
class Response:
    """响应对象,用于处理HTTP请求的响应"""

    status: int = field(default=200, validator=instance_of(int))
    content: bytes = field(validator=instance_of(bytes))
    request: HttpRequest = field(validator=instance_of(HttpRequest))
    headers: Optional[dict] = field(default=None, validator=optional(instance_of(dict)))
    cookies: Optional[dict] = field(default=None, validator=optional(instance_of(dict)))
    browser: Optional[Browser] = field(default=None, validator=optional(instance_of(Browser)))
    text: Optional[str] = field(
        default=None, validator=optional(instance_of(str)), on_setattr=text_setter
    )
    url: Optional[str] = field(default=None, validator=optional(instance_of(str)))
    parser: Optional[Parser] = field(default=None, validator=optional(instance_of(Parser)))
    meta: dict = field(factory=dict, validator=instance_of(dict))
    _cached_data: dict = field(factory=dict, init=False)

    def __attrs_post_init__(self) -> None:
        """初始化响应对象的属性"""
        self.meta = self.request.meta
        self.url = self.request.url.url
        self.request.status = RequestStatus.success if 200 <= self.status < 300 else RequestStatus.failed

        encoding = self.request.encoding or detect(self.content).get("encoding", "utf-8")
        encoding = "GB18030" if encoding and encoding.upper() in ("GBK", "GB2312") else encoding

        if encoding is None:
            encoding = 'utf-8'

        try:
            self.text = self.content.decode(encoding, "replace")
        except MemoryError:
            self.text = self.content.decode(encoding, "ignore")

    def __str__(self) -> str:
        """返回响应对象的字符串表示"""
        help_text = f" {self.request.help}" if self.request.help else ""
        return f"Response {self.request.time}ms <{self.status}{help_text} {self.request.method.value} {self.url}>"

    def __getattr__(self, item: str) -> Any:
        """获取属性值"""
        for field in fields(self.__class__):
            if field.name == item:
                return getattr(self, item)
        if item in self.meta:
            return self.meta[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def re(self, regex: str, flags: int = 0, group: int = None) -> Union[Parser, str, List[str]]:
        """使用正则表达式解析,支持直接获取分组"""
        result = self.parser.re(regex, flags=flags)
        if group is not None:
            return result.get(group=group)
        return result

    def xpath(self, query: str, first: bool = False, **kwargs) -> Union[Parser, str, List[str]]:
        """使用xpath解析,支持直接获取第一个结果"""
        result = self.parser.xpath(query, **kwargs)
        if first:
            return result.get()
        return result
    
    def css(self, query: str, first: bool = False, **kwargs) -> Union[Parser, str, List[str]]:
        """使用css选择器解析,支持直接获取第一个结果"""
        result = self.parser.css(query, **kwargs)
        if first:
            return result.get()
        return result

    @property
    def json(self) -> dict:
        """获取json格式的响应内容"""
        if 'json' not in self._cached_data:
            self._cached_data['json'] = self.parser.json()
        return self._cached_data['json']

    def eval(self, name: str) -> Any:
        """执行js表达式"""
        return self.parser.eval(name)

    def call_method(self, name: str, *args) -> Any:
        """调用js方法"""
        return self.parser.call_method(name, *args)

    def goto(self, wait: float = None) -> None:
        """浏览器跳转到请求url,支持等待时间"""
        if self.browser and self.request:
            self.browser.goto(self.request.url.url)
            if wait:
                self.browser.wait(wait)

    def find_element(self, query: str = None, by: str = By.XPATH, wait: float = None) -> Any:
        """查找单个元素,支持等待时间"""
        if not self.browser:
            return None
        if wait:
            self.browser.wait(wait)
        return self.browser.find_element(query, by)

    def find_elements(self, query: str = None, by: str = By.XPATH, wait: float = None) -> list:
        """查找多个元素,支持等待时间"""
        if not self.browser:
            return None
        if wait:
            self.browser.wait(wait)
        return self.browser.find_elements(query, by)
    
    def render(self, path: Union[str, Path] = None) -> None:
        """在浏览器中渲染响应内容,支持自定义路径"""
        if path:
            tmp_file = Path(path)
        else:
            bin_path = {
                'Windows': Path(r'C:\$Recycle.Bin'),
                'Linux': Path(r'~/.local/share/Trash')
            }.get(platform.system())

            if not bin_path:
                raise AioException('不支持的平台')
            tmp_file = bin_path / 'tmp.html'

        try:
            tmp_file.write_text(self.text, encoding='utf-8')
        except UnicodeEncodeError:
            tmp_file.write_text(self.text, encoding='gbk')

        open_in_browser(tmp_file)

    def render_text(self, wait: float = None) -> None:
        """获取浏览器渲染后的页面内容,支持等待时间"""
        if wait:
            self.browser.wait(wait)
        self.text = self.browser.get_page_source()
        self.parser = Parser(self.text)

    def execute_js(self, js: str, wait: float = None) -> Any:
        """执行js代码,支持等待时间"""
        if wait:
            self.browser.wait(wait)
        return self.browser.execute_js(js)
        
    def parse_json(self, index: str, default: Any = None, callback: callable = None) -> Any:
        """解析json数据"""
        return parse_json_data(self.json, index, default=default, transformations=callback)
