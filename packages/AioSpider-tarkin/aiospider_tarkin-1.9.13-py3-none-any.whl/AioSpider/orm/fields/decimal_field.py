from typing import Optional, Union, Callable

from attrs import define, field

from AioSpider.orm.converters import str_to_float, int_to_float, decimal_to_float
from AioSpider.orm.validators import (
    optional, 
    instance_of, 
    and_validator, 
    is_non_negative,
    ge,
    le,
    not_validator,
    eq
)
from .field import Field, on_setattr

__all__ = [
    'DecimalField', 'FloatField', 'DoubleField'
]


@define(kw_only=True, hash=True, slots=True, str=True, repr=True, eq=True, order=True, auto_exc=True)
class DecimalField(Field):
    """
    Decimal字段类，继承自Field类。用于表示和处理高精度小数。

    属性:
        value (Optional[Decimal]): 字段的值，默认为None
        precision (int): 精度，默认为3
        max_length (int): 最大长度，默认为10
    """
    value: Optional[float] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(float)), on_setattr=on_setattr
    )
    default: Union[None, float, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(float))
    )
    max_length: int = field(
        default=10, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative())
    )
    precision: int = field(
        default=3, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative())
    )
    unsigned: bool = field(default=False, repr=True, kw_only=False, validator=instance_of(bool))
    allow_string: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_int: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_zero: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))

    def _init_default(self) -> None:
        if not self.null and self.default is None:
            self.default = 0.0

    def _init_validators(self):
        validators = super()._init_validators()

        if not self.allow_zero:
            if self.null:
                validators.append(optional(not_validator(eq(0))))
            else:
                validators.append(not_validator(eq(0)))

        if self.unsigned:
            if self.null:
                validators.append(optional(is_non_negative()))
            else:
                validators.append(is_non_negative())

        if self.max_length is not None and self.precision is not None:
            max_value = (10 ** (self.max_length - self.precision)) - 0.1 ** self.precision
            min_value = -max_value
            if self.null:
                validators.append(optional(ge(min_value)))
                validators.append(optional(le(max_value)))
            else:
                validators.append(ge(min_value))
                validators.append(le(max_value))

        return validators
    
    def _init_converters(self):
        converters = super()._init_converters()
        converters.append(decimal_to_float())

        if self.allow_string:
            converters.append(str_to_float())

        if self.allow_int:
            converters.append(int_to_float())

        return converters

    def _set_value(self, value: float) -> float:
        return round(value, self.precision)

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return f"DECIMAL({self.max_length}, {self.precision})"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "DECIMAL" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, hash=True, slots=True, str=True, repr=True, eq=True, order=True, auto_exc=True)
class FloatField(DecimalField):
    """
    Float字段类，继承自DecimalField类。用于表示和处理单精度浮点数。

    属性:
        value (Optional[float]): 字段的值，默认为None
        precision (int): 精度，默认为7
    """

    max_length: Optional[int] = field(
        default=None, repr=True, kw_only=True,
        validator=optional(and_validator(instance_of(int), is_non_negative()))
    )
    precision: int = field(
        default=7, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative())
    )

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return "FLOAT"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "FLOAT"


@define(kw_only=True, hash=True, slots=True, str=True, repr=True, eq=True, order=True, auto_exc=True)
class DoubleField(FloatField):
    """
    Double字段类，继承自FloatField类。用于表示和处理双精度浮点数。

    属性:
        value (Optional[float]): 字段的值，默认为None
        precision (int): 精度，默认为15
    """
    precision: int = field(
        default=15, repr=True, kw_only=True, validator=and_validator(instance_of(int), is_non_negative())
    )

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return "DOUBLE"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "DOUBLE" + (" PRIMARY KEY" if self.primary else "")
