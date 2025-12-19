import difflib
import json
import webbrowser
from typing import Iterable, Union, Any, Optional, List
from urllib.parse import urljoin

import pandas as pd
from lxml import etree
from lxml.etree import _Element, HTML
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup

__all__ = [
    'sanitize_html',
    'extract_xpath',
    'extract_xpath_text',
    'open_in_browser',
    'extract_css',
    'get_absolute_urls',
    'remove_comments',
]


def sanitize_html(html: str, remove_tags: Optional[Iterable] = None, safe_attrs: Optional[Iterable] = None) -> str:
    """
    清理和优化 HTML 文本
    Args:
        html: HTML 文本
        remove_tags: 需要移除的 HTML 标签列表，如：['a', 'p', 'img']
        safe_attrs: 需要保留的属性列表，如：['src', 'href']
    Return:
        清理后的 HTML 文本
    """
    if not html:
        return ''

    remove_tags = frozenset(remove_tags or [])
    safe_attrs = frozenset(safe_attrs or ['src', 'href', 'alt'])

    cleaner = Cleaner(safe_attrs=safe_attrs, remove_tags=remove_tags, style=True, links=False)
    return cleaner.clean_html(html)


def extract_xpath(node: Union[str, _Element], query: str, default: Any = None) -> Union[list, _Element, str]:
    """
    使用 XPath 提取数据
    Args:
        node: 原始 HTML 文本或 lxml 元素
        query: XPath 查询表达式
        default: 默认返回值
    Return:
        default 或 Union[list, _Element, str]
    """
    if not isinstance(node, (str, _Element)) or not isinstance(query, str):
        return default

    try:
        parsed_node = HTML(node) if isinstance(node, str) else node
        return parsed_node.xpath(query)
    except Exception:
        return default


def extract_xpath_text(node: Union[str, _Element], query: str, separator: str = '', default: str = '') -> str:
    """
    使用 XPath 提取文本数据
    Args:
        node: 原始 HTML 文本或 lxml 元素
        query: XPath 查询表达式
        separator: 文本连接符
        default: 默认返回值
    Return:
        XPath 提取出的文本
    """
    text_list = extract_xpath(node=node, query=query, default=default)

    if isinstance(text_list, list):
        return separator.join(text_list) if text_list else default
    if isinstance(text_list, str):
        return text_list
    return default


def open_in_browser(url: str) -> None:
    """
    使用默认浏览器打开网址或文件
    Args:
        url: 网址或文件路径
    """
    webbrowser.open(url)


def extract_css(html: str, selector: str) -> list:
    """
    使用 CSS 选择器提取数据
    Args:
        html: HTML 文本
        selector: CSS 选择器
    Return:
        匹配的元素列表
    """
    soup = BeautifulSoup(html, 'lxml')
    return soup.select(selector)


def get_absolute_urls(base_url: str, html: str) -> list:
    """
    获取 HTML 中所有链接的绝对 URL
    Args:
        base_url: 基础 URL
        html: HTML 文本
    Return:
        绝对 URL 列表
    """
    soup = BeautifulSoup(html, 'lxml')
    return [urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)]


def remove_comments(html: str) -> str:
    """
    移除 HTML 中的注释
    Args:
        html: HTML 文本
    Return:
        移除注释后的 HTML 文本
    """
    return etree.tostring(etree.HTML(html), method='html', encoding='unicode', pretty_print=True, comments=False)


def get_text_content(html: str) -> str:
    """
    提取 HTML 中的纯文本内容
    Args:
        html: HTML 文本
    Return:
        HTML 中的纯文本内容
    """
    soup = BeautifulSoup(html, 'lxml')
    return soup.get_text(separator=' ', strip=True)


def extract_structured_data(html: str) -> dict:
    """
    提取HTML中的结构化数据（JSON-LD）
    Args:
        html: HTML文本
    Return:
        包含结构化数据的字典
    """
    soup = BeautifulSoup(html, 'lxml')
    structured_data = {}
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            structured_data.update(data)
        except json.JSONDecodeError:
            continue
    return structured_data


def extract_meta_tags(html: str) -> dict:
    """
    提取HTML中的meta标签信息
    Args:
        html: HTML文本
    Return:
        包含meta标签信息的字典
    """
    soup = BeautifulSoup(html, 'lxml')
    meta_tags = {}
    for tag in soup.find_all('meta'):
        if 'name' in tag.attrs and 'content' in tag.attrs:
            meta_tags[tag['name']] = tag['content']
    return meta_tags


def clean_html(html: str) -> str:
    """
    清理HTML，移除不安全的标签和属性
    Args:
        html: HTML文本
    Return:
        清理后的HTML文本
    """
    cleaner = Cleaner(
        style=True,
        links=True,
        add_nofollow=True,
        page_structure=False,
        safe_attrs_only=True,
        safe_attrs=frozenset(['src', 'alt', 'href', 'title'])
    )
    return cleaner.clean_html(html)


def extract_tables(html: str) -> List[pd.DataFrame]:
    """
    提取HTML中的表格数据
    Args:
        html: HTML文本
    Return:
        包含表格数据的DataFrame列表
    """
    return pd.read_html(html)


def compare_html_structure(html1: str, html2: str) -> float:
    """
    比较两个HTML文档的结构相似度
    Args:
        html1: 第一个HTML文本
        html2: 第二个HTML文本
    Return:
        结构相似度（0到1之间的浮点数）
    """
    def get_structure(html):
        soup = BeautifulSoup(html, 'lxml')
        return [tag.name for tag in soup.find_all()]
    
    structure1 = get_structure(html1)
    structure2 = get_structure(html2)
    
    similarity = difflib.SequenceMatcher(None, structure1, structure2).ratio()
    return similarity

