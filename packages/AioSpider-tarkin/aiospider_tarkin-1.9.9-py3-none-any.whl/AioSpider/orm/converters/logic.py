from dataclasses import dataclass, field
from typing import Any

from .base import BaseConverter

__all__ = [
    "or_converter",
    "and_converter",
    "not_converter",
]


@dataclass(kw_only=True, slots=True, repr=True)
class OrConverter(BaseConverter):

    converters: list[BaseConverter] = field(default_factory=list, repr=True)
    
    def func(self, value: Any, field_name: str) -> Any:
        for converter in self.converters:
            result = converter(value, field_name)
            if result != value:
                return result
        return value


@dataclass(kw_only=True, slots=True, repr=True)
class AndConverter(BaseConverter):

    converters: list[BaseConverter] = field(default_factory=list, repr=True)
    
    def func(self, value: Any, field_name: str) -> Any:
        for converter in self.converters:
            value = converter(value, field_name)
        return value


@dataclass(kw_only=True, slots=True, repr=True)
class NotConverter(BaseConverter):

    converter: BaseConverter = field(repr=True)

    def func(self, value: Any, field_name: str) -> Any:
        return not self.converter(value, field_name)


def or_converter(*converters: BaseConverter) -> OrConverter:
    """创建一个逻辑或转换器。"""
    return OrConverter(converters=converters)


def and_converter(*converters: BaseConverter) -> AndConverter:
    """创建一个逻辑与转换器。"""
    return AndConverter(converters=converters)


def not_converter(converter: BaseConverter) -> NotConverter:
    """创建一个逻辑非转换器。"""
    return NotConverter(converter=converter)
