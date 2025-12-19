from abc import abstractmethod
from datetime import datetime, date, time
from enum import Enum
from typing import Any, Optional, Tuple, Union, Callable

from attrs import define, field

from AioSpider.orm.validators import (
    optional,
    instance_of,
    iterable_element_of,
    is_non_negative,
    and_validator,
    can_be_none_validator,
    max_length_validator
)
from AioSpider.orm.converters import and_converter, type_converter, non_to_tuple

__all__ = ['Field', 'on_setattr']


def on_setattr(instance: "Field", attribute, value):
    # 如果字段有转换器，则先进行转换
    if attribute.converter:
        value = attribute.converter(value)
    value = instance.convert(value)

    if attribute.validator:
        attribute.validator(instance, attribute, value)
    instance.validate(value)

    return instance.set_value(value)


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class Field:
    """
    基础字段类，用于定义数据模型中的字段属性。
    """
    name: Optional[str] = field(default=None, repr=True, kw_only=True, validator=optional(instance_of(str)))
    value: Any = field(default=None, repr=True, order=True, eq=True, kw_only=True, on_setattr=on_setattr)
    default: Any = field(default=None, repr=True, kw_only=True, converter=lambda x: x() if callable(x) else x)
    column: Optional[str] = field(default=None, repr=True, kw_only=True, validator=optional(instance_of(str)))
    max_length: Optional[int] = field(
        default=None, repr=True, kw_only=True,
        validator=optional(and_validator(instance_of(int), is_non_negative()))
    )
    primary: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    unique: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    index: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    null: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    mark: str = field(default=None, repr=True, kw_only=True, validator=optional(instance_of(str)))
    is_saved: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))
    is_created: bool = field(default=True, repr=True, kw_only=True, validator=instance_of(bool))
    converters: Optional[Union[Callable[[Any, str], Any], Tuple[Callable[[Any, str], Any], ...]]] = field(
        default=None, repr=False, kw_only=True,
        converter=and_converter(non_to_tuple(), type_converter(list, tuple)),
        validator=iterable_element_of(instance_of(Callable))
    )
    validators: Optional[Union[Callable[[Any], Any], Tuple[Callable[[Any], Any], ...]]] = field(
        default=None, repr=False, kw_only=True,
        converter=and_converter(non_to_tuple(), type_converter(list, tuple)),
        validator=iterable_element_of(instance_of(Callable))
    )
    _custom_converter: Optional[Callable] = field(default=None, repr=False, kw_only=True)
    _custom_validator: Optional[Callable[[Any], Any]] = field(default=None, repr=False, kw_only=True)
    _required_default_to_db: bool = field(default=True, validator=instance_of(bool))

    def __get__(self, instance, owner):
        if instance is None:
            return self.value
        return instance._values.get(self.column, self.default)

    def __set__(self, instance, value):
        self.value = value
        instance._values[self.column] = self.value

    def __set_name__(self, owner, name: str) -> None:
        """设置字段名称，并在未指定column时将其设置为name。"""
        self.column = self.column or name

    def __attrs_post_init__(self) -> None:
        """属性初始化后的处理。"""
        self._init_idx()
        self._init_default()
        self.converters = self.converters + tuple(self._init_converters())
        self.validators = self.validators + tuple(self._init_validators())
        if not self.null and self.default is None:
            self._required_default_to_db = False

    def _init_idx(self) -> None:
        """初始化索引相关属性。"""
        if self.primary:
            self.unique = self.index = False
        elif self.unique:
            self.index = False

    @abstractmethod
    def _init_default(self) -> None:
        """初始化默认值（抽象方法）。"""
        pass

    def _init_converters(self) -> list:
        return []

    def _init_validators(self) -> list:
        validators = [
            can_be_none_validator(self.null)
        ]

        if self.max_length is not None:
            validators.append(max_length_validator(self.max_length))

        return validators

    def _set_value(self, value: Any) -> Any:
        return value

    def to_python(self, value):
        return value

    def validate(self, value: Any) -> None:
        """
        验证字段值。

        Args:
            value (Any): 要验证的值。

        Returns:
            Any: 验证后的值或默认值。

        Raises:
            FieldValueValidatorError: 如果值无效或验证失败。
        """

        if not self.validators:
            return None

        for validator in self.validators:
            validator(self, self.column, value)

        if self._custom_validator:
            self._custom_validator(value)

    def convert(self, value: Any) -> Any:
        """
        转换字段值。

        Args:
            value (Any): 要验证的值。

        Returns:
            Any: 验证后的值或默认值。

        Raises:
            FieldValueValidatorError: 如果值无效或验证失败。
        """
        if self._custom_converter is not None:
            value = self._custom_converter(value=value)

        for converter in self.converters:
            value = converter(value, self.column)

        return value

    def set_value(self, value: Any):
        return self._set_value(value) if value is not None else self.default

    def to_mysql(self) -> str:
        """
        生成MySQL建表语句的字段定义部分。
        """
        definition = f"`{self.column}` {self._get_mysql_type()}"
        
        if not self.null:
            definition += " NOT NULL"

        if hasattr(self, 'auto_add') and self.auto_add:
            definition += " DEFAULT CURRENT_TIMESTAMP"

        if hasattr(self, 'auto_now') and self.auto_now:
            definition += " ON UPDATE CURRENT_TIMESTAMP"
            
        if self._required_default_to_db:
            definition += f" DEFAULT {self._format_default_value()}"

        if self.primary:
            definition += " PRIMARY KEY"

        definition += f" COMMENT '{self.mark or self.name}'"
        return definition

    def to_sqlite(self) -> str:
        """
        生成SQLite建表语句的字段定义部分。
        """
        definition = f"`{self.column}` {self._get_sqlite_type()}"

        if not self.null:
            definition += " NOT NULL"

        if hasattr(self, 'auto_add') and self.auto_add:
            definition += " DEFAULT (DATETIME('now', 'localtime'))"

        if self._required_default_to_db:
            definition += f" DEFAULT {self._format_default_value()}"

        return definition

    @classmethod
    def _get_mysql_type(self):
        """
        获取MySQL数据类型。子类应重写此方法以返回特定的MySQL数据类型。
        """
        pass

    @classmethod
    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。子类应重写此方法以返回特定的SQLite数据类型。
        """
        pass

    def _format_default_value(self):
        """
        格式化默认值以用于SQL语句。
        """
        if self.default is None:
            return 'Null'
        if isinstance(self.default, str):
            return f"{self.default!r}"
        if isinstance(self.default, (date, time, datetime)):
            return f"{str(self.default)!r}"
        if isinstance(self.default, Enum):
            return f"{self.default.value!r}"
        return str(self.default)
