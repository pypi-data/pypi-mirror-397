from abc import ABC, abstractmethod
from typing import Any
from contextlib import contextmanager

from AioSpider.exceptions.orm_error import ConverterError

__all__ = ["BaseConverter"]


class BaseConverter(ABC):
    """基础转换器抽象类"""

    @abstractmethod
    def func(self, value: Any, field_name: str) -> Any:
        """
        执行转换操作的抽象方法

        Args:
            value (Any): 需要转换的值

        Returns:
            Any: 转换后的值

        Raises:
            NotImplementedError: 当子类没有实现此方法时抛出
        """
        raise NotImplementedError("子类必须实现convert方法")

    @contextmanager
    def handle_conversion_error(self, value: Any, field_name: str) -> Any:
        try:
            yield
        except Exception as e:
            raise ConverterError(value, field_name or '', str(e))

    def __call__(self, value: Any, field_name: str = None) -> Any:
        """
        使转换器可调用，并处理异常

        Args:
            value (Any): 需要转换的值
            field_name (str): 字段名称，默认为"unknown"

        Returns:
            Any: 转换后的值

        Raises:
            ConversionError: 当转换失败时抛出
        """
        with self.handle_conversion_error(value, field_name):
            return self.func(value, field_name)
