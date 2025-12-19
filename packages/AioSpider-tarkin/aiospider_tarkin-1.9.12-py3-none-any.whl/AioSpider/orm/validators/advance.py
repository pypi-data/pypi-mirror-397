from .base import BaseValidator
from .common import regex_validator
from .logic import or_validator

__all__ = [
    "email_validator",
    "phone_validator",
    "ip_validator",
    "url_validator",
    "uuid_validator"
]


def email_validator() -> BaseValidator:
    """
    创建一个邮箱地址验证器。

    返回:
        BaseValidator: 用于验证邮箱地址的验证器。

    示例:
        >>> validator = email_validator()
        >>> validator(None, None, "user@example.com")   # 不会抛出异常
        >>> validator(None, None, "invalid-email")      # 会抛出 ValueError
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return regex_validator(email_pattern)


def phone_validator() -> BaseValidator:
    """
    创建一个手机号验证器。

    此验证器支持两种格式的手机号：
    1. 中国大陆手机号：以1开头，第二位是3-9之间的数字，后面跟随9位数字。
    2. 香港手机号：以5、6、8或9开头，后面跟随7位数字。

    返回:
        BaseValidator: 手机号验证器实例。

    示例:
        >>> validator = phone_validator()
        >>> validator("13812345678")  # 有效的中国大陆手机号
        >>> validator("98765432")     # 有效的香港手机号
        >>> validator("12345678")     # 抛出 ValueError
    """
    # 中国大陆手机号格式
    mainland_pattern = r'^1[3-9]\d{9}$'
    # 香港手机号格式
    hk_pattern = r'^(5|6|8|9)\d{7}$'
    # 其他国家和地区的手机号格式
    other_patterns = [
        r'^(853)\d{7}$',  # 澳门手机号格式
        r'^(886)\d{8}$',  # 台湾手机号格式
        r'^(82)\d{8}$',   # 韩国手机号格式
        r'^(65)\d{7}$',   # 新加坡手机号格式
        r'^(60)\d{8}$',   # 马来西亚手机号格式
        r'^(66)\d{8}$',   # 泰国手机号格式
        r'^(62)\d{8,9}$', # 印度尼西亚手机号格式
        r'^(63)\d{9}$',   # 菲律宾手机号格式
        r'^(84)\d{8}$',   # 越南手机号格式
        r'^(1)\d{10}$',   # 美国手机号格式
        r'^(1)\d{10}$',   # 加拿大手机号格式
        r'^(61)\d{8}$',   # 澳大利亚手机号格式
        r'^(44)\d{9}$',   # 英国手机号格式
        r'^(31)\d{8}$',   # 荷兰手机号格式
    ]

    return or_validator(
        regex_validator(mainland_pattern),
        regex_validator(hk_pattern),
        *[regex_validator(pattern) for pattern in other_patterns]
    )


def ip_validator() -> BaseValidator:
    """
    创建一个IP地址验证器。

    此验证器可以验证IPv4地址、IPv6地址或两者都验证，取决于传入的ip_type参数。

    返回:
        BaseValidator: IP地址验证器实例。

    示例:
        >>> both_validator = ip_validator()
        >>> both_validator("192.168.0.1")  # 有效
        >>> both_validator("2001:0db8:85a3:0000:0000:8a2e:0370:7334")  # 有效
    """
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    ipv6_pattern = r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'

    return or_validator(regex_validator(ipv4_pattern), regex_validator(ipv6_pattern))


def url_validator() -> BaseValidator:
    """
    创建一个URL验证器。

    返回:
        BaseValidator: 用于验证URL的验证器。

    示例:
        >>> validator = url_validator()
        >>> validator(None, None, "https://www.example.com")  # 不会抛出异常
        >>> validator(None, None, "invalid-url")  # 会抛出 ValueError
    """
    url_pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*(\?[a-zA-Z0-9=&]*)?\/?$'
    return regex_validator(url_pattern)


def uuid_validator() -> BaseValidator:
    """
    创建一个UUID验证器。

    返回:
        BaseValidator: 用于验证UUID的验证器。

    示例:
        >>> validator = uuid_validator()
        >>> validator(None, None, "123e4567-e89b-12d3-a456-426614174000")  # 不会抛出异常
        >>> validator(None, None, "invalid-uuid")  # 会抛出 ValueError
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return regex_validator(uuid_pattern)
