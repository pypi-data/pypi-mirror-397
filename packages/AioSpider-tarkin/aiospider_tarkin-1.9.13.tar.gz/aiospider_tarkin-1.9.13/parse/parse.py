import json
import re
from typing import Optional, TypeVar, Union, Callable, List, Dict, Any

import demjson3
import execjs
from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult, _ElementStringResult
from bs4 import BeautifulSoup, ResultSet, Tag

from AioSpider import logger
from AioSpider.tools import extract_with_regex


XpathParser = TypeVar("XpathParser")
ReParser = TypeVar("ReParser")
CssParser = TypeVar("CssParser")
Parser = TypeVar("Parser")


class BaseParser:
    def __init__(self, content: Union[str, List[str], _Element] = None):
        self.element = content

    def __getitem__(self, index: int) -> 'BaseParser':
        return self.__class__(self.element[index])

    def __len__(self) -> int:
        if isinstance(self.element, list):
            return len(self.element)
        return 1 if self.element is not None else 0

    def is_empty(self) -> bool:
        return not bool(self.element)

    def extract(self) -> List['BaseParser']:
        return [self.__class__(item) for item in (self.element if isinstance(self.element, list) else [self.element])]

    def extract_first(self) -> 'BaseParser':
        if isinstance(self.element, list):
            self.element = self.element[0] if self.element else None
        return self.__class__(self.element)

    def extract_last(self) -> 'BaseParser':
        if isinstance(self.element, list):
            self.element = self.element[-1] if self.element else None
        return self.__class__(self.element)


class XpathParser(BaseParser):
    HTML_ENTITIES = {'&quot;': '"'}

    def __init__(self, content: Union[str, List[str], _Element] = None):
        super().__init__(content)
        if isinstance(content, str):
            self.element = etree.HTML(content)

    def xpath(self, query: str, **kwargs: Dict[str, Any]) -> 'XpathParser':
        if self.element is None:
            return self.__class__()

        if isinstance(self.element, _Element):
            return self.__class__(self.element.xpath(query, **kwargs))

        if isinstance(self.element, list):
            results = [i.xpath(query, **kwargs) for i in self.element if isinstance(i, _Element)]
            return self.__class__([item for sublist in results for item in sublist])

        return self

    def remove_tags(self, tags: Union[str, List[str]]) -> 'XpathParser':
        tags = [tags] if isinstance(tags, str) else tags
        elements = [self.element] if not isinstance(self.element, list) else self.element

        for item in elements:
            if not isinstance(item, _Element):
                continue

            for tag in tags:
                for element in item.xpath(f"//{tag}"):
                    parent = element.getparent()
                    if parent is not None:
                        parent.remove(element)

        return self

    def get_sibling_tags(self, direction: str, tag: Optional[str] = None, n: Optional[int] = None) -> 'XpathParser':
        tag = tag or '*'
        xpath_query = f"{direction}-sibling::{tag}"
        if n is not None:
            xpath_query += f"[{n}]"

        if isinstance(self.element, _Element):
            self.element = self.element.xpath(xpath_query)
        elif isinstance(self.element, list):
            self.element = [j for i in self.element for j in i.xpath(xpath_query)]

        return self

    def get_following_tags(self, tag: Optional[str] = None, n: Optional[int] = None) -> 'XpathParser':
        return self.get_sibling_tags("following", tag, n)

    def get_preceding_tags(self, tag: Optional[str] = None, n: Optional[int] = None) -> 'XpathParser':
        return self.get_sibling_tags("preceding", tag, n)

    def to_string(self, encoding: str = 'unicode', remove_chars: Union[str, List[str]] = '\n') -> str:
        element = self.extract_first()

        if element is None or element.element is None:
            return ''

        try:
            text = etree.tostring(element.element, encoding=encoding)
        except Exception as e:
            logger.error(f"XPath to_string error: {e}")
            return ""

        remove_chars = [remove_chars] if isinstance(remove_chars, str) else remove_chars
        for char in remove_chars:
            text = text.replace(char, '')

        return text

    def text(self) -> str:
        if not self.element:
            return ''

        if isinstance(self.element, (str, _ElementUnicodeResult, _ElementStringResult)):
            text = str(self.element)
        elif isinstance(self.element, _Element):
            text = ''.join(self.element.xpath('*//text()') or [])
        elif isinstance(self.element, list):
            if isinstance(self.element[0], (str, _ElementUnicodeResult, _ElementStringResult)):
                text = ''.join(self.element)
            elif isinstance(self.element[0], _Element):
                text = ''.join(self.element[0].xpath('*//text()') or [])
            else:
                return ''
        else:
            return ''

        for entity, replacement in self.HTML_ENTITIES.items():
            text = text.replace(entity, replacement)

        return text


class ReParser(BaseParser):
    def re(self, pattern: str, flags: int = 0) -> 'ReParser':
        if self.element is None:
            return self

        if isinstance(self.element, str):
            return self.__class__(re.findall(pattern, self.element, flags=flags))

        if isinstance(self.element, list):
            results = [re.findall(pattern, item, flags=flags) for item in self.element if isinstance(item, str)]
            return self.__class__([item for sublist in results for item in sublist])

        return self

    def text(self) -> str:
        if not self.element:
            return ''

        if isinstance(self.element, str):
            return self.element

        if isinstance(self.element, list):
            return self.element[0] if isinstance(self.element[0], str) else ''

        return ''


class CssParser(BaseParser):
    def __init__(self, content: Union[str, List[str]] = None):
        super().__init__(content)
        if isinstance(content, str):
            self.element = BeautifulSoup(content, 'html.parser')

    def css(self, selector: str, **kwargs: Dict[str, Any]) -> 'CssParser':
        if self.element is None:
            return self

        if isinstance(self.element, Tag):
            return self.__class__(self.element.select(selector, **kwargs))

        if isinstance(self.element, ResultSet):
            results = [item.select(selector, **kwargs) for item in self.element if isinstance(item, Tag)]
            return self.__class__([item for sublist in results for item in sublist])

        return self

    def text(self) -> str:
        if isinstance(self.element, str):
            return self.element

        if isinstance(self.element, Tag):
            return str(self.element.string)

        if isinstance(self.element, list):
            if not self.element:
                return ''
            if isinstance(self.element[0], str):
                return self.element[0]
            if isinstance(self.element[0], Tag):
                return str(self.element[0].string)

        return ''
        
    def to_string(self, encoding: str = 'unicode', remove_chars: Union[str, List[str]] = '\n') -> str:
        tag = self.extract_first()

        if tag is None or not isinstance(tag.element, Tag):
            return ''

        text = str(tag.element)

        remove_chars = [remove_chars] if isinstance(remove_chars, str) else remove_chars
        for char in remove_chars:
            text = text.replace(char, '')

        return text

    def attrs(self, key: Optional[str] = None, default: Any = None) -> Union[Dict[str, str], Any]:
        if isinstance(self.element, Tag):
            if key is None:
                return self.element.attrs
            return self.element.attrs.get(key, default)

        if isinstance(self.element, list):
            if key is None:
                attrs = [item.attrs for item in self.element if isinstance(item, Tag)]
            else:
                attrs = [item.attrs.get(key, default) for item in self.element if isinstance(item, Tag)]
            
            if not attrs:
                return default
            return attrs[0] if len(attrs) == 1 else attrs

        return default


class Parser:
    HTML_ENTITIES = {
        '&quot;': '"'
    }

    def __init__(self, content: str = None):
        self._content = content
        self._js_context = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._content})'

    def __getitem__(self, index: int) -> 'Parser':
        return self.__class__(self._content[index])

    def __len__(self) -> int:
        return len(self._content) if self._content else 0

    __repr__ = __str__

    @property
    def text(self) -> str:
        if self._content is None:
            return ''
        if isinstance(self._content, str):
            return self._content
        text = self._content.text()
        for entity, replacement in self.HTML_ENTITIES.items():
            text = text.replace(entity, replacement)
        return text

    def json(self) -> Dict[str, Any]:
        def parse_json(content: str, max_attempts: int = 3) -> Dict[str, Any]:
            for _ in range(max_attempts):
                try:
                    try:
                        return json.loads(content)
                    except:
                        return demjson3.decode(content)
                except demjson3.JSONDecodeError:
                    # 如果直接解析失败，尝试解析JSONP
                    match = re.match(r'^[\w\s$]+\s*\((.*)\)', content.strip(), re.S)
                    if match:
                        content = match.group(1)
                        continue

                    # 移除Unicode转义
                    content = re.sub(r'\\u[\da-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), content)
                    # 如果解析失败，尝试移除非法字符
                    content = re.sub(r'[^\x20-\x7E]', '', content)

            return {}

        text = self.strip_text()
        return parse_json(text) if text else {}

    def strip_text(self, chars: Optional[str] = None, callback: Optional[Callable[[str], str]] = None) -> str:
        text = self.text.strip() if chars is None else self.text.strip(chars)
        return callback(text) if callback is not None else text
    
    @property
    def js_context(self):
        if self._js_context is None:
            self._js_context = execjs.compile(self.text)
        return self._js_context

    def eval_js(self, expression: str) -> Any:
        return self.js_context.eval(expression)

    def call_js_method(self, method_name: str, *args: Any) -> Any:
        return self.js_context.call(method_name, *args)

    def extract_first(self) -> 'Parser':
        return self.__class__(self._content.extract_first())

    def extract_last(self) -> 'Parser':
        return self.__class__(self._content.extract_last())

    def extract(self) -> List['Parser']:
        return [self.__class__(item) for item in self._content.extract()]
    
    def extract_text(self) -> List[str]:
        return [self.__class__(item).text for item in self._content.extract()]

    def re(self, pattern: str, flags: int = 0) -> 'Parser':
        if self._content is None:
            return self

        if isinstance(self._content, ReParser):
            return self.__class__(self._content.re(pattern, flags=flags))

        return self.__class__(ReParser(self.text).re(pattern, flags=flags))

    def xpath(self, query: str, **kwargs: Dict[str, Any]) -> 'Parser':
        if self._content is None:
            return self

        if isinstance(self._content, XpathParser):
            return self.__class__(self._content.xpath(query, **kwargs))

        return self.__class__(XpathParser(self.text).xpath(query, **kwargs))

    def css(self, selector: str, **kwargs: Dict[str, Any]) -> 'Parser':
        if self._content is None:
            return self

        if isinstance(self._content, CssParser):
            return self.__class__(self._content.css(selector, **kwargs))

        return self.__class__(CssParser(self._content).css(selector, **kwargs))

    @property
    def is_empty(self) -> bool:
        return self._content.is_empty()

    def remove_tags(self, tags: Union[str, List[str]]) -> 'Parser':
        if isinstance(self._content, XpathParser):
            self._content = self._content.remove_tags(tags)
        return self

    def get_following_tags(self, tag: Optional[str] = None, n: Optional[int] = None) -> 'Parser':
        if isinstance(self._content, XpathParser):
            self._content = self._content.get_following_tags(tag=tag, n=n)
        return self

    def get_preceding_tags(self, tag: Optional[str] = None, n: Optional[int] = None) -> 'Parser':
        if isinstance(self._content, XpathParser):
            self._content = self._content.get_preceding_tags(tag=tag, n=n)
        return self

    def to_string(self, encoding: str = 'unicode', remove_chars: Union[str, List[str]] = '\n') -> str:
        if isinstance(self._content, (XpathParser, CssParser)):
            return self._content.to_string(encoding=encoding, remove_chars=remove_chars)
        return ''
    
    def attrs(self, key: Optional[str] = None, default: Any = None) -> Union[Dict[str, str], Any]:
        if isinstance(self._content, CssParser):
            return self.__class__(self._content.attrs(key=key, default=default))
        return None
