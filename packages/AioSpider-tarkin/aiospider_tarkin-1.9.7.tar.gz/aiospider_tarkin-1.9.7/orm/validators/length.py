import operator
from typing import Any, Callable

from dataclasses import field, dataclass

from .base import BaseValidator
from AioSpider.exceptions.orm_error import FieldValueValidatorError

__all__ = [
    "min_length_validator",
    "max_length_validator",
]


@dataclass(kw_only=True, slots=True, repr=True)
class LengthValidator(BaseValidator):
    """
    长度验证器类，用于验证可计算长度的对象是否满足特定的长度条件。

    这个验证器可以用于检查字符串、列表、元组等具有 __len__ 方法的对象的长度。
    它可以被配置为检查最小长度或最大长度。

    属性:
        length (int): 用于比较的长度值。
        compare_func (Callable[[int, int], bool]): 用于比较长度的函数，接受两个整数参数并返回布尔值。

    示例:
        >>> validator = LengthValidator(5, lambda x, y: x >= y, "大于或等于")
        >>> validator(None, field(name="username"), "user1")  # 不会抛出异常
        >>> validator(None, field(name="username"), "u")  # 会抛出 ValidationError
    """
    length: int = field(repr=True)
    compare_func: Callable[[int, int], bool] = field(repr=True)

    def __call__(self, instance: Any, attribute: field, value: Any) -> None:
        """
        执行长度验证。

        参数:
            instance (Any): 被验证的实例，通常不使用但可能在某些情况下有用。
            attribute (field): 被验证的属性，用于生成错误消息。
            value (Any): 被验证的值，必须是可测量长度的对象（如字符串、列表等）。

        抛出:
            ValidationError: 如果值的长度不符合验证器的要求，抛出包含详细信息的异常。

        注意:
            此方法假设 value 对象有 __len__ 方法。如果传入的 value 不支持 len() 函数，将会引发 TypeError。
        """
        if isinstance(value, str) and not self.compare_func(len(value), self.length):
            raise FieldValueValidatorError(
                field_name=attribute if isinstance(attribute, str) else attribute.name,
                value=value,
                rule=self.compare_func.__name__,
                validator_name=self.__class__.__name__
            )


def min_length_validator(length: int) -> LengthValidator:
    """
    创建一个最小长度验证器。

    此函数返回一个 LengthValidator 实例，用于验证值的长度是否大于或等于指定的最小长度。

    参数:
        length (int): 要验证的最小长度。

    返回:
        LengthValidator: 配置为验证最小长度的长度验证器实例。

    示例:
        >>> validator = min_length(5)
        >>> validator(None, field(name="username"), "user1")  # 不会抛出异常
        >>> validator(None, field(name="username"), "u")  # 会抛出 ValueError

    注意:
        返回的验证器可以直接用作 attrs 库的字段验证器。
    """
    return LengthValidator(
        length=length,
        compare_func=operator.ge,
    )


def max_length_validator(length: int) -> LengthValidator:
    """
    创建一个最大长度验证器。

    此函数返回一个 LengthValidator 实例，用于验证值的长度是否小于或等于指定的最大长度。

    参数:
        length (int): 要验证的最大长度。

    返回:
        LengthValidator: 配置为验证最大长度的长度验证器实例。

    示例:
        >>> validator = max_length(10)
        >>> validator(None, field(name="username"), "user1")  # 不会抛出异常
        >>> validator(None, field(name="username"), "very_long_username")  # 会抛出 ValueError

    注意:
        返回的验证器可以直接用作 attrs 库的字段验证器。
    """
    return LengthValidator(
        length=length,
        compare_func=operator.le,
    )
