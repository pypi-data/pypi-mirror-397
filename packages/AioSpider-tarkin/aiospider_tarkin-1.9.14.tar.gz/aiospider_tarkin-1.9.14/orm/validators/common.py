import re
from enum import Enum
from typing import Any, Union, Optional, Callable, Iterable, TypeVar, Type, Tuple

from dataclasses import dataclass, field, Field

from .base import BaseValidator
from AioSpider.exceptions.orm_error import FieldTypeValidatorError, FieldValueValidatorError, ValidationError

__all__ = [
    "instance_of",
    "subclass_of",
    "optional",
    "regex_validator",
    "is_callable",
    "iterable_element_of",
    "deep_mapping",
    "can_be_none_validator",
    "can_be_empty_validator",
    "enum_validator"
]

T = TypeVar('T')


@dataclass(kw_only=True, slots=True, repr=True)
class InstanceOfValidator(BaseValidator):
    """
    验证器类，用于检查实例是否为指定类型。

    属性:
        expected_type (Union[Type[T], Tuple[Type, ...]]): 期望的类型或类型元组。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            检查给定的值是否为期望的类型。

    抛出:
        FieldTypeValidatorError: 如果值不是期望的类型。
    """
    expected_type: Union[Type[T], Tuple[Type, ...]] = field(repr=True)

    def __call__(self, instance: Any, attribute, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise FieldTypeValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                expected_type=self.expected_type,
                validator_name=self.__class__.__name__
            )


@dataclass(kw_only=True, slots=True, repr=True)
class SubclassOfValidator(BaseValidator):
    """
    子类验证器类，用于检查类是否为指定类型的子类。

    属性:
        expected_type (Union[Type[T], Tuple[Type[T], ...]]): 期望的父类或父类元组。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            检查给定的值是否为期望父类的子类。

    抛出:
        FieldTypeValidatorError: 如果值不是期望父类的子类。
    """
    expected_type: Union[Type[T], Tuple[Type[T], ...]] = field(repr=True)

    def __call__(self, instance: Any, attribute, value: Any) -> None:
        if not issubclass(value, self.expected_type):
            raise FieldTypeValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                expected_type=self.expected_type,
                validator_name=self.__class__.__name__
            )


@dataclass(kw_only=True, slots=True, repr=True)
class OptionalValidator(BaseValidator):
    """
    验证器类，允许值为 None 或满足指定的验证器。

    属性:
        validator (Callable[[Any, field, Any], None]): 用于非 None 值的验证器。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            如果值不为 None，则应用指定的验证器。
    """
    validator: Callable[[Any, field, Any], None] = field(repr=True)

    def __call__(self, instance: Any, attribute: Union[Field, str], value: Any) -> None:
        if value is not None:
            self.validator(instance, attribute, value)


@dataclass(kw_only=True, slots=True, repr=True)
class MatchesReValidator(BaseValidator):
    """
    正则表达式匹配验证器类。

    属性:
        pattern (re.Pattern): 用于匹配的正则表达式模式。
        match_func (Callable[[str], Optional[re.Match]]): 用于执行匹配的函数。

    方法:
        __call__(self, instance: Any, attribute: field, value: str) -> None:
            检查给定的值是否匹配指定的正则表达式模式。

    抛出:
        ValueError: 如果值不匹配指定的正则表达式模式。
    """
    pattern: re.Pattern = field(repr=True)
    match_func: Callable[[re.Pattern, str], Optional[str]] = field(repr=True)

    def __call__(self, instance: Any, attribute, value: str) -> None:
        instance_of(str)(instance, attribute, value)
        if not self.match_func(self.pattern, value):
            raise FieldValueValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                rule=self.pattern.pattern,
                validator_name=self.__class__.__name__
            )


class IsCallableValidator(BaseValidator):
    """
    验证器类，检查值是否可调用。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            检查给定的值是否可调用。

    抛出:
        TypeError: 如果值不可调用。
    """

    def __call__(self, instance: Any, attribute, value: Any) -> None:
        if not callable(value):
            raise FieldTypeValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                expected_type="可调用类型",
                validator_name=self.__class__.__name__
            )


@dataclass(kw_only=True, slots=True, repr=True)
class IterableValidator(BaseValidator):
    """
    验证器类，用于深度验证可迭代对象的成员。

    属性:
        member_validator (Callable[[Any, field, Any], None]): 用于验证每个成员的验证器。
    """
    member_validator: Callable[[Any, field, Any], None] = field(repr=True)

    def __call__(self, instance: Any, attribute: Union[Field, str], value: Iterable[Any]) -> None:
        instance_of(Iterable)(instance, attribute, value)
        for member in value:
            self.member_validator(instance, attribute, member)


@dataclass(kw_only=True, slots=True, repr=True)
class MappingValidator(BaseValidator):
    """
    验证器类，用于深度验证映射对象的键和值。

    属性:
        key_validator (Callable[[Any, field, Any], None]): 用于验证每个键的验证器。
        value_validator (Callable[[Any, field, Any], None]): 用于验证每个值的验证器。
    """
    key_validator: Callable[[Any, field, Any], None] = field(repr=True)
    value_validator: Callable[[Any, field, Any], None] = field(repr=True)

    def __call__(self, instance: Any, attribute: Union[Field, str], value: Any) -> None:
        instance_of(dict)(instance, attribute, value)
        for key, val in value.items():
            self.key_validator(instance, attribute, key)
            self.value_validator(instance, attribute, val)


def instance_of(*expected_type: Type) -> InstanceOfValidator:
    """
    创建一个验证器，用于检查实例是否为指定类型。

    参数:
        expected_type (Union[Type[T], Tuple[Type, ...]]): 期望的类型或类型元组。

    返回:
        InstanceOfValidator: 用于验证实例类型的验证器。

    示例:
        >>> validator = instance_of(int)
        >>> validator(None, None, 5)  # 不会抛出异常
        >>> validator(None, None, "5")  # 会抛出 TypeError
        >>> validator = instance_of(int, float)
        >>> validator(None, None, 5)  # 不会抛出异常
        >>> validator(None, None, 5.5)  # 不会抛出异常
    """
    return InstanceOfValidator(expected_type=expected_type)


def subclass_of(expected_type: Union[Type[T], Tuple[Type[T], ...]]) -> SubclassOfValidator:
    """
    创建一个子类验证器。

    参数:
        expected_type (Union[Type[T], Tuple[Type[T], ...]]): 期望的父类或父类元组。

    返回:
        SubclassOfValidator: 用于验证子类关系的验证器。

    示例:
        >>> class A: pass
        >>> class B(A): pass
        >>> validator = subclass_of(A)
        >>> validator(None, None, B)  # 不会抛出异常
        >>> validator(None, None, int)  # 会抛出 TypeError
    """
    return SubclassOfValidator(expected_type=expected_type)


def optional(validator: BaseValidator) -> OptionalValidator:
    """
    创建一个验证器，允许值为 None 或满足指定的验证器。

    参数:
        validator (Union[Callable[[Any, field, Any], None], Iterable[Callable[[Any, field, Any], None]]]):
            用于非 None 值的验证器或验证器列表。

    返回:
        OptionalValidator: 允许 None 值或应用指定验证器的验证器。

    注意:
        如果传入多个验证器，它们将被组合成一个使用 and 逻辑的验证器。

    示例:
        >>> def int_validator(instance, attribute, value):
        ...     if not isinstance(value, int):
        ...         raise TypeError("Must be an int")
        >>> validator = optional(int_validator())
        >>> validator(None, None, None)  # 不会抛出异常
        >>> validator(None, None, 5)  # 不会抛出异常
        >>> validator(None, None, "5")  # 会抛出 TypeError
    """
    return OptionalValidator(validator=validator)


def regex_validator(
        regex: Union[str, re.Pattern],
        func: Optional[Callable] = None,
        flags: int = 0
) -> MatchesReValidator:
    """
    创建一个正则表达式匹配验证器。

    参数:
        regex (Union[str, re.Pattern]): 用于匹配的正则表达式字符串或已编译的模式。
        func (Optional[Callable], optional): 用于执行匹配的函数。可以是 re.match, re.search, re.fullmatch 或 None。
            如果为 None，默认使用 re.fullmatch。
        flags (int, optional): 用于编译正则表达式的标志。默认为 0。

    返回:
        MatchesReValidator: 用于验证字符串是否匹配指定正则表达式的验证器。

    抛出:
        ValueError: 如果提供的 func 不是有效的匹配函数。

    示例:
        >>> validator = regex_validator(r'\d{3}-\d{2}-\d{4}')
        >>> validator(None, None, '123-45-6789')  # 不会抛出异常
        >>> validator(None, None, '12-345-6789')  # 会抛出 ValueError
    """
    valid_funcs = {None: re.fullmatch, re.fullmatch: re.fullmatch, re.search: re.search, re.match: re.match}
    if func not in valid_funcs:
        raise ValidationError(
            validator_name=regex_validator.__name__,
            message=f"'func' 参数必须是 {', '.join(f.__name__ if f else 'None' for f in valid_funcs)} 其中之一"
        )

    pattern = regex if isinstance(regex, re.Pattern) else re.compile(regex, flags)
    match_func = valid_funcs[func]

    return MatchesReValidator(pattern=pattern, match_func=match_func)


def is_callable() -> IsCallableValidator:
    """
    创建一个验证器，检查值是否可调用。

    返回:
        IsCallableValidator: 用于验证值是否可调用的验证器。

    示例:
        >>> validator = is_callable()
        >>> validator(None, None, lambda x: x)  # 不会抛出异常
        >>> validator(None, None, "not callable")  # 会抛出 TypeError
    """
    return IsCallableValidator()


def iterable_element_of(member_validator: Callable[[Any, field, Any], None]) -> IterableValidator:
    """
    创建一个验证器，用于深度验证可迭代对象的成员。

    参数:
        member_validator (Callable[[Any, field, Any], None]): 用于验证每个成员的验证器。

    返回:
        IterableValidator: 用于深度验证可迭代对象的验证器。

    注意:
        如果 member_validator 是一个可迭代对象，其中的验证器将被组合成一个使用 and 逻辑的验证器。

    示例:
        >>> def int_validator(instance, attribute, value):
        ...     if not isinstance(value, int):
        ...         raise TypeError("Must be an int")
        >>> validator = iterable_element_of(int_validator())
        >>> validator(None, None, [1, 2, 3])  # 不会抛出异常
        >>> validator(None, None, [1, '2', 3])  # 会抛出 TypeError
    """
    return IterableValidator(member_validator=member_validator)


def deep_mapping(
        key_validator: Callable[[Any, field, Any], None],
        value_validator: Callable[[Any, field, Any], None],
) -> MappingValidator:
    """
    创建一个深度映射验证器。

    此函数返回一个 DeepMapping 验证器，用于深度验证映射对象（如字典）的键和值。

    参数:
        key_validator (Callable[[Any, field, Any], None]):
            用于验证每个键的验证器函数。此函数应接受实例、属性和值作为参数。

        value_validator (Callable[[Any, field, Any], None]):
            用于验证每个值的验证器函数。此函数应接受实例、属性和值作为参数。

    返回:
        MappingValidator: 一个 MappingValidator 验证器实例，可用于深度验证映射对象。

    示例:
        >>> def str_validator(instance, attribute, value):
        ...     if not isinstance(value, str):
        ...         raise TypeError("Must be a string")
        >>> def int_validator(instance, attribute, value):
        ...     if not isinstance(value, int):
        ...         raise TypeError("Must be an integer")
        >>> validator = deep_mapping(str_validator, int_validator)
        >>> validator(None, None, {"a": 1, "b": 2})     # 不会抛出异常
        >>> validator(None, None, {"a": "1", "b": 2})   # 会抛出 TypeError
        >>> validator(None, None, {1: 1, "b": 2})       # 会抛出 TypeError
    """
    return MappingValidator(key_validator=key_validator, value_validator=value_validator)


def can_be_none_validator(null: bool):
    """
    创建一个验证器，检查值是否不为 None。

    参数:
        null (bool): 是否允许 None 值。

    返回:
        BaseValidator: 用于验证值是否不为 None 的验证器。
    """

    def validator(instance: Any, attribute, value: Any) -> None:
        if value is None and not null:
            raise FieldValueValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                rule='不能为None',
                validator_name=can_be_none_validator.__name__
            )

    return validator


def can_be_empty_validator(empty: bool):
    """
    创建一个验证器，检查值是否不为空。

    参数:
        empty (bool): 是否允许空值。

    返回:
        BaseValidator: 用于验证值是否不为空的验证器。
    """

    def validator(instance: Any, attribute, value: Any) -> None:
        if value == '' and not empty:
            raise FieldValueValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                rule='不能为空字符串',
                validator_name=can_be_empty_validator.__name__
            )

    return validator


def enum_validator(choices: Type[Enum]):
    def validator(instance, attribute, value) -> None:
        if value not in choices:
            raise FieldValueValidatorError(
                field_name=instance.column or instance.name,
                value=value,
                rule='当前值不在美剧范围中',
                validator_name=enum_validator.__name__
            )
    return validator

