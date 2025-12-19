import uuid
from enum import Enum
from hashlib import md5
from typing import Optional, Union, Callable, List, Tuple, Type

from attrs import define, field

from AioSpider.orm.validators import (
    optional,
    instance_of,
    and_validator,
    or_validator,
    is_non_negative,
    le,
    ip_validator,
    uuid_validator,
    phone_validator,
    email_validator,
    url_validator,
    enum_validator,
    subclass_of
)
from AioSpider.orm.converters import (
    and_converter,
    non_to_list,
    str_to_list,
    type_converter,
    str_to_enum,
)
from .field import Field, on_setattr
from .string_field import CharField
from .decimal_field import DecimalField

__all__ = [
    'HashField',
    'IPAddressField',
    'IPAddressField',
    'UUIDField',
    'EmailField',
    'PhoneNumberField',
    'URLField',
    'EnumField',
    'PriceField'
]


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class HashField(CharField):
    """
    哈希字段类，用于处理和验证哈希值。

    属性:
        make_hash_field (Optional[Union[str, List[str], Tuple[str, ...]]]): 用于生成哈希的字段
        exclude_field (Optional[Union[str, List[str], Tuple[str, ...]]]): 排除在哈希计算之外的字段
    """
    max_length: int = field(
        default=32, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )
    min_length: int = field(
        default=32, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative())
    )
    make_hash_field: Optional[Union[str, List[str], Tuple[str, ...]]] = field(
        default=None, repr=True, kw_only=True,
        converter=and_converter(non_to_list(), str_to_list(), type_converter(tuple, list)),
        validator=optional(instance_of(list))
    )
    unique: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))
    null: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    exclude_field: Optional[Union[str, List[str], Tuple[str, ...]]] = field(
        default=None, repr=True, kw_only=True,
        converter=and_converter(non_to_list(), str_to_list(), type_converter(tuple, list)),
        validator=optional(instance_of(list))
    )

    def __get__(self, instance, owner):
        fields = self._get_hash_fields(instance)
        value_list = [str(getattr(instance, f, None)) for f in fields]
        setattr(instance, self.column, self._calculate_hash(value_list))
        return self.value

    def _get_hash_fields(self, instance):
        all_fields = list(instance.fields.keys())
        hash_fields = self.make_hash_field or all_fields
        exclude_fields = self.exclude_field
        exclude_fields.append('id')
        exclude_fields.extend([k for k, v in instance.fields.items() if isinstance(v, self.__class__)])
        return [f for f in hash_fields if f not in exclude_fields]

    @staticmethod
    def _calculate_hash(value_list: list) -> Optional[str]:
        if not value_list:
            return None
        return md5('-'.join(value_list).encode('utf-8')).hexdigest()


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class IPAddressField(Field):
    """
    IP地址字段类，用于处理和验证IP地址。

    属性:
        value (Optional[str]): 字段的值，默认为None
        default (Optional[str]): 默认值，默认为None
    """
    value: Optional[str] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(and_validator(instance_of(str), ip_validator())), on_setattr=on_setattr
    )
    default: Union[None, str, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(str))
    )
    max_length: int = field(
        default=39, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )

    def _init_default(self):
        if not self.null and self.default is None:
            self.default = ""

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


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class UUIDField(Field):
    """
    UUID字段类，用于处理和验证UUID。

    属性:
        value (Optional[UUID]): 字段的值，默认为None
        default (Optional[str]): 默认值，默认为None
    """
    value: Optional[uuid.UUID] = field(
        factory=uuid.uuid4, repr=True, order=True, eq=True, kw_only=True,
        converter=lambda x: str(x) if isinstance(x, uuid.UUID) else x,
        validator=optional(or_validator(instance_of(str), uuid_validator())), on_setattr=on_setattr
    )

    def __get__(self, instance, owner):
        setattr(instance, self.column, self.value)
        return self.value

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return f"CHAR(36)"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TEXT" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class EmailField(Field):
    """
    电子邮件字段类，用于验证和存储电子邮件地址。

    属性:
        value (Optional[str]): 字段的值，默认为None
        default (Optional[str]): 默认值，默认为None
    """
    value: Optional[str] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(and_validator(instance_of(str), email_validator())), on_setattr=on_setattr
    )
    default: Union[None, str, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(str))
    )
    max_length: int = field(
        default=80, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative())
    )

    def _init_default(self) -> None:
        if not self.null and self.default is None:
            self.default = ""

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return f"VARCHAR({self.max_length})"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TEXT"


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class PhoneNumberField(Field):
    """
    电话号码字段类，用于验证和存储电话号码。

    属性:
        value (Optional[str]): 字段的值，默认为None
        default (Optional[str]): 默认值，默认为None
        max_length (int): 电话号码的最大长度，默认为11
    """
    value: Optional[str] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(and_validator(instance_of(str), phone_validator())), on_setattr=on_setattr
    )
    default: Union[None, str, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(str))
    )
    max_length: int = field(
        default=11, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )

    def _init_default(self) -> None:
        if not self.null and self.default is None:
            self.default = ""

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


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class URLField(CharField):
    """
    URL字段类，用于验证和存储URL。

    属性:
        value (Optional[str]): 字段的值，默认为None
        max_length (int): URL的最大长度，默认为2000
    """
    value: Optional[str] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(and_validator(instance_of(str), url_validator())), on_setattr=on_setattr
    )
    max_length: int = field(
        default=2000, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class PriceField(DecimalField):
    """
    价格字段类，用于验证和存储价格。
    """
    unsigned: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class EnumField(Field):
    """
    枚举字段类，用于验证和存储枚举值。

    属性:
        choices (Union[List[str], Tuple[str, ...]]): 可选的枚举值列表
        value (Optional[str]): 字段的值，默认为None
    """
    value: Optional[Union[Enum, str]] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(Enum, str)), on_setattr=on_setattr
    )
    default: Optional[Union[Enum, str]] = field(
        default=None, repr=True, kw_only=True,
        validator=optional(instance_of(Enum, str))
    )
    choices: Type[Enum] = field(repr=True, kw_only=True, validator=subclass_of(Enum))
    max_length: int = field(
        default=20, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )

    def _init_validators(self) -> List:
        validators = super()._init_validators()
        validators.append(enum_validator(self.choices))
        return validators

    def _init_converters(self) -> list:
        converters = super()._init_converters()
        converters.append(str_to_enum(self.choices))
        return converters

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        if self.max_length <= 255:
            return f"VARCHAR({self.max_length})"
        elif self.max_length <= 65535:
            return "TEXT"
        else:
            return "LONGTEXT"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TEXT" + (" PRIMARY KEY" if self.primary else "")
