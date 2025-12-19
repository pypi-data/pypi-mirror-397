from typing import Optional, Union, Callable

from attr import define, field

from AioSpider.orm.validators import (
    optional,
    instance_of,
    and_validator,
    is_non_negative,
    le
)
from .field import Field, on_setattr

__all__ = [
    'TinyBlobField', 'BlobField', 'MediumBlobField', 'LongBlobField'
]


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class TinyBlobField(Field):
    """
    字节内容字段类，用于处理和验证字节类型的数据。

    属性:
        value (Optional[bytes]): 字段的值，默认为None
        default (Optional[bytes]): 默认值，默认为None
    """
    value: Optional[bytes] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(bytes)), on_setattr=on_setattr
    )
    default: Union[None, bytes, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(bytes))
    )
    max_length: int = field(
        default=65535, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(255))
    )

    def _init_default(self):
        if not self.null and self.default is None:
            self.default = b""

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return "TINYBLOB"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TINYBLOB" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class BlobField(TinyBlobField):
    max_length: int = field(
        default=65535, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return "BLOB"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "BLOB" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class MediumBlobField(BlobField):
    max_length: int = field(
        default=16777215, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(16777215))
    )

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return "MEDIUMBLOB"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "MEDIUMBLOB" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class LongBlobField(BlobField):
    """
    长文本字段类，用于处理和验证长文本数据。

    属性:
        max_length (int): 文本的最大长度，默认为4294967295 (2^32 - 1)
    """
    max_length: int = field(
        default=4294967295, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(4294967295))
    )

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        return "LONGBLOB"

    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "LONGBLOB" + (" PRIMARY KEY" if self.primary else "")
