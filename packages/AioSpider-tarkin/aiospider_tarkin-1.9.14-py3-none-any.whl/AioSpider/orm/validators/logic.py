from typing import Any, Callable, Tuple
from dataclasses import dataclass, field

from .base import BaseValidator
from AioSpider.exceptions.orm_error import ValidationError

__all__ = [
    "and_validator",
    "not_validator",
    "or_validator",
    "in_validator",
]


@dataclass(kw_only=True, slots=True, repr=True)
class AndValidator(BaseValidator):
    """
    与验证器类，用于组合多个验证器，所有验证器都必须通过。

    这个验证器将多个验证器组合在一起，只有当所有的验证器都通过时，整体验证才会通过。
    如果任何一个验证器失败，将会抛出相应的异常。

    属性:
        validators (Tuple[Callable[[Any, field, Any], None], ...]): 
            一个包含多个验证器函数的元组。每个验证器函数应接受实例、属性和值作为参数。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            执行与验证。对给定的值应用所有验证器。

    示例:
        >>> def positive(instance, attribute, value):
        ...     if value <= 0:
        ...         raise ValueError("Must be positive")
        >>> def even(instance, attribute, value):
        ...     if value % 2 != 0:
        ...         raise ValueError("Must be even")
        >>> validator = AndValidator(validators=(positive, even))
        >>> validator(None, field(name="age"), 4)    # 通过
        >>> validator(None, field(name="age"), -2)   # 抛出 ValueError
        >>> validator(None, field(name="age"), 3)    # 抛出 ValueError
    """
    validators: Tuple[Callable[[Any, field, Any], None], ...] = field(default=(), repr=True)

    def __call__(self, instance: Any, attribute: field, value: Any) -> None:
        """
        执行与验证。

        对给定的值应用所有验证器。如果任何验证器失败，将会抛出相应的异常。

        参数:
            instance (Any): 被验证的实例。
            attribute (field): 被验证的属性。
            value (Any): 被验证的值。

        抛出:
            Exception: 如果任何验证器失败，将抛出相应的异常。
        """
        for validator in self.validators:
            validator(instance, attribute, value)


@dataclass(kw_only=True, slots=True, repr=True)
class NotValidator(BaseValidator):
    """
    非验证器类，用于反转验证器的结果。

    这个验证器接受一个验证器作为参数，并反转其结果。
    如果原始验证器通过，NotValidator 将抛出异常；
    如果原始验证器抛出异常，NotValidator 将通过验证。

    属性:
        validator (Callable[[Any, field, Any], None]): 
            要被反转的原始验证器函数。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            执行非验证。反转原始验证器的结果。

    示例:
        >>> def even(instance, attribute, value):
        ...     if value % 2 != 0:
        ...         raise ValueError("Must be even")
        >>> validator = NotValidator(validator=even)
        >>> validator(None, None, 3)  # 通过
        >>> validator(None, None, 2)  # 抛出 ValueError
    """
    validator: Callable[[Any, field, Any], None] = field(repr=True)

    def __call__(self, instance: Any, attribute: field, value: Any) -> None:
        """
        执行非验证。

        反转原始验证器的结果。如果原始验证器通过，则抛出异常；
        如果原始验证器抛出异常，则通过验证。

        参数:
            instance (Any): 被验证的实例。
            attribute (field): 被验证的属性。
            value (Any): 被验证的值。

        抛出:
            ValueError: 如果原始验证器通过，则抛出此异常。
        """
        try:
            self.validator(value)
        except Exception:
            return
        raise ValidationError(
            validator_name=self.__class__.__name__,
            message=f"{attribute.name} 字段不符合 {self.validator!r} 验证规则"
        )


@dataclass(kw_only=True, slots=True, repr=True)
class OrValidator(BaseValidator):
    """
    或验证器类，用于组合多个验证器，只要有一个验证器通过即可。

    这个验证器将多个验证器组合在一起，只要其中一个验证器通过，整体验证就会通过。
    只有当所有验证器都失败时，才会抛出异常。

    属性:
        validators (Tuple[Callable[[Any, field, Any], None], ...]): 
            一个包含多个验证器函数的元组。每个验证器函数应接受实例、属性和值作为参数。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            执行或验证。尝试所有验证器，直到一个通过或全部失败。

    示例:
        >>> def even(instance, attribute, value):
        ...     if value % 2 != 0:
        ...         raise ValueError("Must be even")
        >>> def positive(instance, attribute, value):
        ...     if value <= 0:
        ...         raise ValueError("Must be positive")
        >>> validator = OrValidator(validators=(even, positive))
        >>> validator(None, field(name="age"), 2)   # 通过
        >>> validator(None, field(name="age"), 3)   # 通过
        >>> validator(None, field(name="age"), -2)  # 通过
        >>> validator(None, field(name="age"), -1)  # 抛出 ValueError
    """
    validators: Tuple[Callable[[Any, field, Any], None], ...] = field(default=(), repr=True)

    def __call__(self, instance: Any, attribute: field, value: Any) -> None:
        """
        执行或验证。

        尝试所有验证器，直到一个通过或全部失败。如果所有验证器都失败，
        将抛出一个包含所有错误信息的异常。

        参数:
            instance (Any): 被验证的实例。
            attribute (field): 被验证的属性。
            value (Any): 被验证的值。

        抛出:
            ValueError: 如果所有验证器都失败，则抛出此异常，包含所有错误信息。
        """
        errors = []
        for validator in self.validators:
            try:
                validator(instance, attribute, value)
                return
            except Exception as e:
                errors.append(str(e))
        raise ValidationError(
            validator_name=self.__class__.__name__,
            message=f"{attribute.name} 字段验证失败，所有验证器都未能通过对值 {value!r} 的验证。错误信息：{', '.join(errors)}"
        )


@dataclass(kw_only=True, slots=True, repr=True)
class InValidator(BaseValidator):
    """
    验证器类，检查值是否在指定的选项中。

    这个验证器检查给定的值是否存在于预定义的选项集合中。
    如果值不在选项中，将抛出 ValueError。

    属性:
        options (Tuple[Any, ...]): 
            一个包含所有有效选项的元组。

    方法:
        __call__(self, instance: Any, attribute: field, value: Any) -> None:
            检查值是否在指定的选项中。

    示例:
        >>> validator = InValidator(options=(1, 2, 3))
        >>> validator(None, field(name="test"), 2)  # 通过
        >>> validator(None, field(name="test"), 4)  # 抛出 ValueError
    """
    options: Tuple[Any, ...] = field(repr=True)

    def __call__(self, instance: Any, attribute: field, value: Any) -> None:
        """
        检查值是否在指定的选项中。

        如果值不在预定义的选项中，将抛出 ValueError。

        参数:
            instance (Any): 被验证的实例。
            attribute (field): 被验证的属性。
            value (Any): 被验证的值。

        抛出:
            ValueError: 如果值不在指定的选项中，则抛出此异常。
        """
        if value not in self.options:
            raise ValidationError(
                validator_name=self.__class__.__name__,
                message=f"{attribute.name} 字段必须在 {self.options!r} 范围内，但是您设置的值是 {value!r}"
            )


def and_validator(*validators: Callable[[Any, field, Any], None]) -> AndValidator:
    """
    创建一个与验证器。

    这个函数是 AndValidator 类的便捷构造器。

    参数:
        *validators (Callable[[Any, field, Any], None]): 
            一个或多个验证器函数。

    返回:
        AndValidator: 一个新的 AndValidator 实例。

    示例:
        >>> def positive(instance, attribute, value):
        ...     if value <= 0:
        ...         raise ValueError("Must be positive")
        >>> def even(instance, attribute, value):
        ...     if value % 2 != 0:
        ...         raise ValueError("Must be even")
        >>> validator = and_validator(positive, even)
        >>> validator(None, field(name="age"), 4)   # 通过
        >>> validator(None, field(name="age"), -2)  # 抛出 ValueError
    """
    return AndValidator(validators=validators)


def not_validator(validator: Callable[[Any, field, Any], None]) -> NotValidator:
    """
    创建一个非验证器。

    这个函数是 NotValidator 类的便捷构造器。

    参数:
        validator (Callable[[Any, field, Any], None]): 
            要被反转的原始验证器函数。

    返回:
        NotValidator: 一个新的 NotValidator 实例。

    示例:
        >>> def even(instance, attribute, value):
        ...     if value % 2 != 0:
        ...         raise ValueError("Must be even")
        >>> validator = not_validator(even)
        >>> validator(None, field(name="age"), 3)  # 通过
        >>> validator(None, field(name="age"), 2)  # 抛出 ValueError
    """
    return NotValidator(validator=validator)


def or_validator(*validators: Callable[[Any, field, Any], None]) -> OrValidator:
    """
    创建一个或验证器。

    这个函数是 OrValidator 类的便捷构造器。

    参数:
        *validators (Callable[[Any, field, Any], None]): 
            一个或多个验证器函数。

    返回:
        OrValidator: 一个新的 OrValidator 实例。

    示例:
        >>> def even(instance, attribute, value):
        ...     if value % 2 != 0:
        ...         raise ValueError("Must be even")
        >>> def positive(instance, attribute, value):
        ...     if value <= 0:
        ...         raise ValueError("Must be positive")
        >>> validator = or_validator(even, positive)
        >>> validator(None, field(name="age"), 2)   # 通过
        >>> validator(None, field(name="age"), 3)   # 通过
        >>> validator(None, field(name="age"), -2)  # 通过
        >>> validator(None, field(name="age"), -1)  # 抛出 ValueError
    """
    return OrValidator(validators=validators)


def in_validator(options: Tuple[Any, ...]) -> InValidator:
    """
    创建一个验证器，检查值是否在指定的选项中。

    这个函数是 InValidator 类的便捷构造器。

    参数:
        options (Tuple[Any, ...]): 
            一个包含有效选项的可迭代对象。

    返回:
        InValidator: 一个新的 InValidator 实例。

    示例:
        >>> validator = in_validator([1, 2, 3])
        >>> validator(None, field(name="test"), 2)  # 通过
        >>> validator(None, field(name="test"), 4)  # 抛出 ValueError
    """
    return InValidator(options=tuple(options))
