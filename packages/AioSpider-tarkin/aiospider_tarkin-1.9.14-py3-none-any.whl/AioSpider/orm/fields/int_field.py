from typing import Optional, Any, Type, Union, Callable

from attrs import define, field

from ..converters import type_converter, str_to_int, float_to_int
from AioSpider.orm.validators import (
    optional,
    instance_of,
    and_validator,
    is_non_negative as non_negative,
    ge,
    le,
    can_be_none_validator,
    is_non_negative,
    not_validator,
    eq
)
from .field import Field, on_setattr

__all__ = [
    'IntField',
    'TinyIntField',
    'SmallIntField',
    'MediumIntField',
    'BigIntField',
    'AutoIntField',
    'BooleanField'
]


@define(kw_only=True, hash=True, slots=True, str=True, repr=True, eq=True, order=True, auto_exc=True)
class IntField(Field):
    """
    整数字段类，继承自Field类。用于表示和处理整数类型的数据。

    属性:
        value (Optional[int]): 整数值，默认为None
        default (Optional[int]): 默认值，默认为None
        max_length (int): 最大长度，默认为11
        unsigned (bool): 是否无符号，默认为False
        min_value (Optional[int]): 最小值，默认为None
        max_value (Optional[int]): 最大值���默认为None
    """
    value: Optional[int] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True, validator=optional(instance_of(int)),
        on_setattr=on_setattr
    )
    default: Union[None, int, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(int))
    )
    max_length: int = field(
        default=11, repr=True, kw_only=True, validator=and_validator(instance_of(int), non_negative())
    )
    unsigned: bool = field(default=False, repr=True, kw_only=False, validator=instance_of(bool))
    min_value: Optional[int] = field(default=None, repr=True, kw_only=True, validator=optional(instance_of(int)))
    max_value: Optional[int] = field(default=None, repr=True, kw_only=True, validator=optional(instance_of(int)))
    allow_string: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_float: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_zero: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))
    
    _min_bit_value: Optional[int] = field(default=None, init=False, repr=False)
    _max_bit_value: Optional[int] = field(default=None, init=False, repr=False)

    def __attrs_post_init__(self):
        self._min_bit_value = None
        self._max_bit_value = None
        self._set_min_max_bit_value()
        super().__attrs_post_init__()

    def _get_bit(self):
        return 32

    def _init_default(self):
        """
        初始化默认值。如果字段不允许为空且默认值为None，则设置默认值为0。
        """
        if not self.null and self.default is None:
            self.default = 0

    def _set_min_max_bit_value(self):
        bit = self._get_bit()
        if self.unsigned:
            self._min_bit_value = 0
            self._max_bit_value = (1 << bit) - 1
        else:
            self._min_bit_value = -(1 << (bit - 1))
            self._max_bit_value = (1 << (bit - 1)) - 1

    def _init_converters(self):
        converters = super()._init_converters()
        if self.allow_string:
            converters.append(str_to_int())
        if self.allow_float:
            converters.append(float_to_int())
        return converters

    def _init_validators(self):

        validators = [
            can_be_none_validator(self.null)
        ]

        if not self.allow_zero:
            validators.append(not_validator(eq(0)))

        if self.unsigned:
            if self.null:
                validators.append(optional(is_non_negative()))
            else:
                validators.append(is_non_negative())

        if self.min_value is not None:
            if self.null:
                validators.append(optional(ge(max(self._min_bit_value, self.min_value))))
            else:
                validators.append(ge(max(self._min_bit_value, self.min_value)))
        else:
            if self.null:
                validators.append(optional(ge(self._min_bit_value)))
            else:
                validators.append(ge(self._min_bit_value))

        if self.max_value is not None:
            if self.null:
                validators.append(optional(le(min(self._max_bit_value, self.max_value))))
            else:
                validators.append(le(min(self._max_bit_value, self.max_value)))
        else:
            if self.null:
                validators.append(optional(le(self._max_bit_value)))
            else:
                validators.append(le(self._max_bit_value))

        return validators

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"INT({self.max_length}){unsigned_str}"

    def _get_sqlite_type(self):
        return "INTEGER" + (" PRIMARY KEY" if self.primary else "")


class TinyIntField(IntField):
    """TinyInt字段类，继承自IntField类。用于表示和处理小范围整数（8位）。"""

    def _get_bit(self):
        """
        初始化后的处理方法。设置bit值，然后调用父类的初始化后处理方法。
        """
        return 8

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"TINYINT({self.max_length}){unsigned_str}"
    
    def _get_sqlite_type(self):
        return "TINYINT" + (" PRIMARY KEY" if self.primary else "")


class SmallIntField(IntField):
    """SmallInt字段类，继承自IntField类。用于表示和处理中等范围整数（16位）。"""

    def _get_bit(self):
        """
        初始化后的处理方法。设置bit值，然后调用父类的初始化后处理方法。
        """
        return 16

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"SMALLINT({self.max_length}){unsigned_str}"
    
    def _get_sqlite_type(self):
        return "SMALLINT" + (" PRIMARY KEY" if self.primary else "")


class MediumIntField(IntField):
    """MediumInt字段类，继承自IntField类。用于表示和处理较大范围整数（24位）。"""

    def _get_bit(self):
        """
        初始化后的处理方法。设置bit值，然后调用父类的初始化后处理方法。
        """
        return 24

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"MEDIUMINT({self.max_length}){unsigned_str}"
    
    def _get_sqlite_type(self):
        return "MEDIUMINT" + (" PRIMARY KEY" if self.primary else "")


class BigIntField(IntField):
    """BigInt字段类，继承自IntField类。用于表示和处理大范围整数（64位）。"""

    def _get_bit(self):
        """
        初始化后的处理方法。设置bit值，然后调用父类的初始化后处理方法。
        """
        return 64

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"BIGINT({self.max_length}){unsigned_str}"

    def _get_sqlite_type(self):
        return "BIGINT" + (" PRIMARY KEY" if self.primary else "")
    
    
@define(kw_only=True, slots=True, str=True, repr=True, eq=True, auto_exc=True)
class AutoIntField(IntField):
    """
    自增整数字段类，继承自IntField类。用于自动生成递增的整数值。

    属性:
        step (int): 自增步长，默认为1
    """

    current_value: Optional[int] = field(
        default=0, repr=True, order=True, eq=True, kw_only=True, validator=optional(instance_of(int)),
        on_setattr=on_setattr
    )
    unsigned: bool = field(default=True, repr=True, kw_only=False, validator=instance_of(bool))
    step: int = field(default=1, repr=True, validator=and_validator(instance_of(int), non_negative()))
    null: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    _required_default_to_db: bool = field(default=False, validator=instance_of(bool))
    _inited: bool = field(default=False, init=False, repr=False)

    def __get__(self, instance: Any, owner: Type[Any]):
        if instance is None:
            return self
            
        # 检查是否需要初始化
        if not self._inited and self.column == 'id':
            self.current_value = owner.Meta.init_id - 1
            self._inited = True
            
        if self.column not in instance._values:
            self.current_value += self.step
            instance._values[self.column] = self.current_value
            
        return instance._values[self.column]

    def __set__(self, instance: Any, value: int):
      instance._values[self.column] = value

    def _get_bit(self):
        return 32

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"INT({self.max_length}){unsigned_str} AUTO_INCREMENT"

    def _get_sqlite_type(self):
        return "INTEGER" + (" PRIMARY KEY" if self.primary else "") + " AUTOINCREMENT" 


@define(kw_only=True, slots=True, str=True, repr=True, eq=True, auto_exc=True)
class BooleanField(TinyIntField):
    """
    布尔字段类，继承自TinyIntField类。用于表示和处理布尔值（使用整数0和1表示）。

    属性:
        value (Optional[Union[int, bool]]): 布尔值，使用整数表示（0为False，1为True）
    """
    value: Optional[Union[int, bool]] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True, converter=type_converter(bool, int),
        validator=optional(instance_of(int, bool)), on_setattr=on_setattr
    )
    default: Union[None, int, bool, Callable] = field(
        default=False, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(int, bool))
    )
    max_length: int = field(
        default=1, repr=True, kw_only=True, validator=and_validator(instance_of(int), non_negative())
    )
    unsigned: bool = field(default=False, repr=True, kw_only=False, validator=instance_of(bool))

    def _init_default(self):
        if not self.null and self.default is None:
            self.default = 0

    def _get_mysql_type(self):
        unsigned_str = " UNSIGNED" if self.unsigned else ""
        return f"TINYINT({self.max_length}){unsigned_str}"

    def _get_sqlite_type(self):
        return "TINYINT" + (" PRIMARY KEY" if self.primary else "")
