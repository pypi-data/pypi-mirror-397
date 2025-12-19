from typing import Any, Union, Callable
import operator

from dataclasses import field, dataclass

from .base import BaseValidator
from AioSpider.exceptions.orm_error import FieldValueValidatorError

__all__ = [
    "lt",
    "le",
    "ge",
    "gt",
    "eq",
    "is_positive",
    "is_non_negative",
    "magnitude"
]


@dataclass(kw_only=True, slots=True, repr=True)
class NumberValidator(BaseValidator):
    """
    数值比较验证器类。

    此类用于创建各种数值比较验证器，如小于、小于等于、大于、大于等于等。

    属性:
        bound (Union[int, float]): 比较的边界值。
        compare_op (str): 比较操作符的字符串表示，用于错误消息。
        compare_func (Callable[[Any, Any], bool]): 实际执行比较的函数。

    示例:
        >>> validator = NumberValidator(10, "<=", operator.le)
        >>> validator(None, field(name="age"), 9)  # 不会抛出异常
        >>> validator(None, field(name="age"), 11)  # 会抛出 ValueError
    """
    bound: Union[int, float] = field(repr=True)
    compare_op: str = field(repr=True)
    compare_func: Callable[[Any, Any], bool] = field(repr=True)

    def __call__(self, instance: Any, attribute: field, value: Any) -> None:
        """
        执行数值比较验证。

        参数:
            instance (Any): 被验证的实例，通常不使用。
            attribute (field): 被验证的属性，用于错误消息。
            value (Any): 被验证的值。

        抛出:
            ValidationError: 如果比较失败，抛出包含详细信息的异常。
        """
        if not self.compare_func(value, self.bound):
            raise FieldValueValidatorError(
                field_name=attribute if isinstance(attribute, str) else attribute.name,
                value=value,
                rule=f"{self.compare_op} {self.bound}",
                validator_name=self.__class__.__name__
            )


def lt(val: Union[int, float]) -> NumberValidator:
    """
    创建一个小于验证器。

    此函数返回一个 NumberValidator 实例，用于验证值是否小于指定的边界值。

    参数:
        val (Union[int, float]): 比较的边界值。

    返回:
        NumberValidator: 配置为"小于"比较的数值验证器实例。

    示例:
        >>> validator = lt(5)
        >>> validator(None, field(name="score"), 4)  # 不会抛出异常
        >>> validator(None, field(name="score"), 5)  # 会抛出 ValueError
    """
    return NumberValidator(bound=val, compare_op="<", compare_func=operator.lt)


def le(val: Union[int, float]) -> NumberValidator:
    """
    创建一个小于等于验证器。

    此函数返回一个 NumberValidator 实例，用于验证值是否小于或等于指定的边界值。

    参数:
        val (Union[int, float]): 比较的边界值。

    返回:
        NumberValidator: 配置为"小于等于"比较的数值验证器实例。

    示例:
        >>> validator = le(5)
        >>> validator(None, field(name="score"), 5)  # 不会抛出异常
        >>> validator(None, field(name="score"), 6)  # 会抛出 ValueError
    """
    return NumberValidator(bound=val, compare_op="<=", compare_func=operator.le)


def ge(val: Union[int, float]) -> NumberValidator:
    """
    创建一个大于等于验证器。

    此函数返回一个 NumberValidator 实例，用于验证值是否大于或等于指定的边界值。

    参数:
        val (Union[int, float]): 比较的边界值。

    返回:
        NumberValidator: 配置为"大于等于"比较的数值验证器实例。

    示例:
        >>> validator = ge(5)
        >>> validator(None, field(name="score"), 5)  # 不会抛出异常
        >>> validator(None, field(name="score"), 4)  # 会抛出 ValueError
    """
    return NumberValidator(bound=val, compare_op=">=", compare_func=operator.ge)


def gt(val: Union[int, float]) -> NumberValidator:
    """
    创建一个大于验证器。

    此函数返回一个 NumberValidator 实例，用于验证值是否大于指定的边界值。

    参数:
        val (Union[int, float]): 比较的边界值。

    返回:
        NumberValidator: 配置为"大于"比较的数值验证器实例。

    示例:
        >>> validator = gt(5)
        >>> validator(None, field(name="score"), 6)  # 不会抛出异常
        >>> validator(None, field(name="score"), 5)  # 会抛出 ValueError
    """
    return NumberValidator(bound=val, compare_op=">", compare_func=operator.gt)


def eq(val: Union[int, float]) -> NumberValidator:
    """
    创建一个等于验证器。

    此函数返回一个NumberValidator实例，用于验证输入值是否等于指定的值。

    参数:
        val (Union[int, float]): 比较的目标值。

    返回:
        NumberValidator: 配置为"等于"比较的验证器实例。

    示例:
        >>> validator = eq(5)
        >>> validator(5)  # 不会抛出异常
        >>> validator(4)  # 抛出ValueError
        >>> validator(6)  # 抛出ValueError
    """
    return NumberValidator(bound=val, compare_op="==", compare_func=operator.eq)



def is_positive() -> NumberValidator:
    """
    创建一个正数验证器。

    此函数返回一个 NumberValidator 实例，用于验证值是否为正数（大于0）。

    返回:
        NumberValidator: 配置为验证正数的数值验证器实例。

    示例:
        >>> validator = is_positive()
        >>> validator(None, field(name="count"), 1)  # 不会抛出异常
        >>> validator(None, field(name="count"), 0)  # 会抛出 ValueError
        >>> validator(None, field(name="count"), -1)  # 会抛出 ValueError
    """
    return gt(0)


def is_non_negative() -> NumberValidator:
    """
    创建一个非负数验证器。

    此函数返回一个 NumberValidator 实例，用于验证值是否为非负数（大于或等于0）。

    返回:
        NumberValidator: 配置为验证非负数的数值验证器实例。

    示例:
        >>> validator = is_non_negative()
        >>> validator(None, field(name="count"), 0)  # 不会抛出异常
        >>> validator(None, field(name="count"), 1)  # 不会抛出异常
        >>> validator(None, field(name="count"), -1)  # 会抛出 ValueError
    """
    return ge(0)


def magnitude(level: int) -> NumberValidator:
    """
    创建一个数量级验证器。

    此函数返回一个NumberValidator实例，用于验证输入值是否在指定的数量级范围内。
    数量级是指10的幂次方，例如1、10、100、1000等。

    参数:
        level (int): 指定的数量级。例如，2表示两位数，3表示三位数。

    返回:
        NumberValidator: 配置为验证指定数量级的验证器实例。

    示例:
        >>> validator = magnitude(2)
        >>> validator(10)   # 不会抛出异常
        >>> validator(99)   # 不会抛出异常
        >>> validator(9)    # 抛出ValueError
        >>> validator(100)  # 抛出ValueError
    """
    lower = 10 ** (level - 1)
    upper = 10 ** level - 1

    def validate_magnitude(value: Union[int, float], _upper: Union[int, float]) -> bool:
        return lower <= abs(value) <= _upper

    return NumberValidator(bound=upper, compare_op="in", compare_func=validate_magnitude)

