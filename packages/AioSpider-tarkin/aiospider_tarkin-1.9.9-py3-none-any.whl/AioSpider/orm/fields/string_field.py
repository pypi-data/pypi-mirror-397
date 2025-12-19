from pathlib import Path
from typing import Any, Optional, Dict, Union, Tuple, Pattern, Callable

from attrs import define, field

from AioSpider.orm.validators import (
    optional,
    instance_of,
    and_validator,
    is_non_negative,
    le,
    min_length_validator,
    max_length_validator,
    regex_validator,
    can_be_none_validator,
    can_be_empty_validator
)
from ..converters import (
    type_converter, 
    str_to_pattern, 
)
from .field import Field, on_setattr

__all__ = [
    'CharField',
    'PathField',
    'ExtensionNameField',
]


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class CharField(Field):
    """
    字符串字段类，用于处理和验证字符串类型的数据。

    属性:
        value (Optional[str]): 字段的值，默认为None
        max_length (int): 字符串的最大长度，默认为255
        min_length (int): 字符串的最小长度，默认为0
        default (Optional[str]): 默认值，默认为None
        is_truncate (bool): 是否在超过最大长度时截断字符串，默认为False
        choices (Optional[Union[Dict[Any, str], Tuple[Tuple[Any, str], ...]]]): 
            可选的选项集合，可以是字典或元组形式，默认为None
        regex (Optional[Union[str, Pattern[str]]]): 用于验证的正则表达式，可以是字符串或编译后的正则表达式对象，默认为None
        strip (bool): 是否去除字符串两端的空白字符，默认为True
        blank (bool): 是否允许空字符串，默认为False
        validator_chain (ValidatorChain): 验证器链，用于组合多个验证规则

    示例:
        >>> name_field = CharField(max_length=50, min_length=2)
        >>> gender_field = CharField(choices={"M": "Male", "F": "Female"})
        >>> email_field = CharField(regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    """
    value: Optional[str] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(str)), on_setattr=on_setattr
    )
    max_length: int = field(
        default=255, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )
    min_length: int = field(
        default=0, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative())
    )
    default: Union[None, str, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(str))
    )
    blank: bool = field(default=True, repr=False, kw_only=True, validator=instance_of(bool))
    is_truncate: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    choices: Optional[Union[Dict[Any, str], Tuple[Tuple[Any, str], ...]]] = field(
        default=None, repr=True, kw_only=True, converter=type_converter(tuple, dict),
        validator=optional(instance_of(dict))
    )
    regex: Optional[Union[str, Pattern[str]]] = field(
        default=None, repr=True, kw_only=True, converter=str_to_pattern(),
        validator=optional(instance_of(Pattern))
    )
    strip: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))

    def _init_default(self) -> None:
        """
        初始化默认值。
        如果字段不允许为空且不允许空字符串，且没有设置默认值，则将默认值设为空字符串。
        """
        if not self.null and self.default is None:
            if self.blank:
                self.default = ""
            else:
                self._required_default_to_db = False

    def _init_validators(self) -> list:
        """
        初始化验证器链。
        """

        validators = [
            can_be_none_validator(self.null),
            can_be_empty_validator(self.blank)
        ]

        if self.min_length >= 0:
            validators.append(min_length_validator(self.min_length))
        if self.max_length >= 0 and not self.is_truncate:
            validators.append(max_length_validator(self.max_length))
        if self.regex:
            validators.append(regex_validator(self.regex))

        return validators

    def _set_value(self, value: str) -> str:
        if self.choices:
            value = self.choices.get(value, value)

        if self.strip:
            value = value.strip()

        if self.is_truncate and len(value) > self.max_length:
            value = value[:self.max_length]

        return value

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        if self.max_length == self.min_length and self.max_length <= 255:
            return f"CHAR({self.max_length})" + (" PRIMARY KEY" if self.primary else "")
        else:
            return f"VARCHAR({self.max_length})" + (" PRIMARY KEY" if self.primary else "")

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TEXT" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class PathField(CharField):
    """
    路径字段类，用于处理和验证路径类型的数据。

    属性:
        value (Optional[Union[str, Path]]): 字段的值，默认为None
        max_length (int): 字符串的最大长度，默认为255
        min_length (int): 字符串的最小长度，默认为0
        default (Optional[Union[str, Path]]): 默认值，默认为None
        is_truncate (bool): 是否在超过最大长度时截断字符串，默认为False
        regex (Optional[Union[str, Pattern[str]]]): 用于验证的正则表达式，可以是字符串或编译后的正则表达式对象，默认为None
        strip (bool): 是否去除字符串两端的空白字符，默认为True

    示例:
        >>> path_field = PathField(max_length=100, min_length=1)
        >>> unix_path = PathField(regex=r'^(/[^/ ]*)+/?$')
    """
    value: Optional[Union[str, Path]] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True, converter=type_converter(str, Path),
        validator=optional(instance_of(Path, str)), on_setattr=on_setattr
    )
    max_length: int = field(
        default=150, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )

    def __attrs_post_init__(self) -> None:
        if self.regex is None:
            self.regex = r'^(?:[a-zA-Z]:\\|/)?(?:[^\\\r\n]+[\\/]?)*$'
        super().__attrs_post_init__()
    
    def _init_converters(self) -> list:
        converters = super()._init_converters()
        converters.append(type_converter(Path, str))
        return converters

    def exists(self) -> bool:
        """
        检查路径是否存在。

        返回:
            bool: 如果路径存在返回True，否则返回False
        """
        return self.value is not None and self.value.exists()

    def __truediv__(self, other: Union[str, Path]) -> 'PathField':
        """
        实现路径的拼接操作。

        参数:
            other (Union[str, Path]): 要拼接的路径

        返回:
            PathField: 拼接后的新PathField实例
        """
        if isinstance(other, str):
            other = Path(other)

        return PathField(
            name=self.name,
            max_length=self.max_length,
            min_length=self.min_length,
            default=self.default,
            null=self.null,
            regex=self.regex,
            strip=self.strip,
            value=self.value / other if self.value else other
        )


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class ExtensionNameField(Field):
    """
    扩展名字段类，用于处理和验证文件扩展名。

    属性:
        value (Optional[str]): 字段的值，默认为None
        default (Optional[str]): 默认值，默认为".txt"
        strip (bool): 是否去除字符串两端的空白字符，默认为True
    """
    value: str = field(
        default="", repr=True, order=True, eq=True, kw_only=True,
        converter=lambda x: f'.{x.lstrip(".")}',
        validator=instance_of(str), on_setattr=on_setattr
    )
    default: Union[str, Callable] = field(
        default=".txt", repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=instance_of(str)
    )
    strip: bool = field(default=True, validator=instance_of(bool))
    max_length: int = field(
        default=20, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )

    def __attrs_post_init__(self) -> None:
        """
        初始化后的处理方法。设置默认值并调用父类的初始化后处理方法。
        """
        self.null = False
        super().__attrs_post_init__()

    def _init_default(self):
        pass

    def _set_value(self, value: str) -> str:
        if self.strip:
            value = f'.{value.strip().lstrip(".")}'
        return value

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return f"VARCHAR({self.max_length})"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TEXT" + (" PRIMARY KEY" if self.primary else "")
