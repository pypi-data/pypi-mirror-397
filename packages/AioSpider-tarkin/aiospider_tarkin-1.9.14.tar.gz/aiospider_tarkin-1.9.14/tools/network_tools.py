import ipaddress
import socket
from urllib import parse
from typing import Dict, Optional

import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

__all__ = [
    'parse_url_params',
    'get_base_url',
    'get_url_path',
    'parse_cookies',
    'encode_url_params',
    'build_url_with_params',
    'is_valid_ip',
    'get_domain_ip',
    'create_retry_session',
    'normalize_url',
]


def parse_url_params(url: str) -> Dict[str, str]:
    """
    从 URL 中解析查询参数
    Args:
        url: 完整的 URL 字符串
    Returns:
        包含查询参数的字典
    """
    parsed_url = parse.urlparse(url)
    return dict(parse.parse_qsl(parsed_url.query))


def get_base_url(url: str) -> str:
    """
    从 URL 中提取基础 URL（协议 + 域名 + 路径）
    Args:
        url: 完整的 URL 字符串
    Returns:
        基础 URL 字符串
    """
    parsed_url = parse.urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'


def get_url_path(url: str) -> str:
    """
    从 URL 中提取路径
    Args:
        url: 完整的 URL 字符串
    Returns:
        URL 路径字符串
    """
    return parse.urlparse(url).path


def parse_cookies(cookies_string: str) -> Dict[str, str]:
    """
    解析 cookies 字符串为字典
    Args:
        cookies_string: cookies 文本字符串，通常从浏览器请求头中复制
    Returns:
        解析后的 cookies 字典
    """
    return {
        item.split('=')[0].strip(): item.split('=')[-1].strip()
        for item in cookies_string.split(';')
        if '=' in item and item.split('=')[0].strip() and item.split('=')[-1].strip()
    }


def encode_url_params(params: Dict[str, str]) -> str:
    """
    将参数字典编码为 URL 查询字符串
    Args:
        params: 参数字典
    Returns:
        编码后的查询字符串
    """
    return parse.urlencode(sorted(params.items()))


def build_url_with_params(base_url: str, params: Dict[str, str]) -> str:
    """
    构建带参数的完整 URL
    Args:
        base_url: 基础 URL
        params: 参数字典
    Returns:
        完整的 URL 字符串
    """
    return f"{base_url}?{encode_url_params(params)}"


def is_valid_ip(ip: str) -> bool:
    """
    验证 IP 地址是否有效
    Args:
        ip: IP 地址字符串
    Returns:
        布尔值，表示 IP 是否有效
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_domain_ip(domain: str) -> Optional[str]:
    """
    获取域名对应的 IP 地址
    Args:
        domain: 域名字符串
    Returns:
        IP 地址字符串，如果解析失败则返回 None
    """
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def create_retry_session(
        retries: int = 3, backoff_factor: float = 0.3, status_forcelist: Optional[list] = None
) -> requests.Session:
    """
    创建一个带有重试机制的 requests 会话
    Args:
        retries: 最大重试次数
        backoff_factor: 重试间隔的计算因子
        status_forcelist: 需要重试的 HTTP 状态码列表
    Returns:
        配置了重试机制的 requests.Session 对象
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist or [429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def normalize_url(url: str) -> str:
    """
    规范化 URL（移除多余的斜杠，添加协议等）
    Args:
        url: 输入的 URL 字符串
    Returns:
        规范化后的 URL 字符串
    """
    parsed = parse.urlparse(url)
    scheme = parsed.scheme or 'http'
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ''
    normalized = parse.urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))
    return normalized.rstrip('/')
