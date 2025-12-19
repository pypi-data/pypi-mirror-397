from abc import ABC, abstractmethod
from dataclasses import field, Field
from typing import Any, Union

__all__ = ["BaseValidator"]


class BaseValidator(ABC):

    @abstractmethod
    def __call__(self, instance: Any, attribute: Union[Field, str], value: Any) -> None:
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} validator>"
